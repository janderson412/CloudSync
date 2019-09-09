import os
import sqlite3
from datetime import datetime
from enum import Enum

import boto3


class S3StorageClass(Enum):
    """
    Enumeration of Amazon S3 storage types.
    """
    STANDARD = 1
    REDUCED_REDUNDANCY = 2
    GLACIER = 3
    STANDARD_IA = 4
    ONEZONE_IA = 5
    INTELLIGENT_TIERING = 6
    DEEP_ARCHIVE = 7


class FileObject:
    """
    A FileObject contains information about a single object stored in the cloud.  This is an abstract class
    that is realized with an Amazon S3 file object or filesystem file object.
    """

    def __init__(self, size=0, timestamp=datetime.now(), path_delimiter='/', full_name=None, name=None, folder=None):
        """

        :param size: (long) Size of file object in bytes (default: 0)
        :param timestamp: (datetime) Timestamp of file object (default: current time)
        :param path_delimiter: (string) delimiter for components of file path (default: '/'
        :param full_name: (string) Full name of file object, including path (relative to root of repository)
        :param name: (string) Name of file object (without path)
        :param folder: (string) Folder containing file object
        """
        if full_name is None and (name is None or folder is None):
            raise Exception('Full path not given and either name or folder missing')
        if full_name is not None and (name is not None or folder is not None):
            raise Exception('Full name given and either name or folder are defined')
        if size < 0:
            raise Exception('Size must be greater than or equal to 0')
        if full_name is not None:
            # full pathname given
            self._full_name = full_name
            self._name = full_name.split(path_delimiter)[-1]
            folder_size = len(full_name) - len(self._name) - 1
            self._folder = full_name[0:folder_size]
        else:
            # folder and name given separately
            self._name = name
            self._folder = folder
            self._full_name = folder + path_delimiter + name
        self._size = size
        self._timestamp = timestamp

    @property
    def name(self):
        """
        Get the name of the object, without the full path.

        :returns: (string) Name of object (key)
        """
        return self._name

    @property
    def full_name(self):
        """
        Get the full pathname of the file object.

        :return: (string) Full pathname of file object.
        """
        return self._full_name

    @property
    def folder(self):
        return self._folder

    @property
    def size(self):
        """
        Get the size of the object.

        :return: (int) Size of object, in bytes
        """
        return self._size

    @property
    def timestamp(self):
        """
        Get the date & time object was stored.

        :return: (datetime) Date/time when object stored.
        """
        return self._timestamp


class Repository:
    """
    A repository for holding FileObjects.
    """

    def __init__(self, file_objects, supports_versions=False):
        """

        :param file_objects:
        """
        self._file_objects = file_objects
        self._supports_versions = supports_versions

    @property
    def file_objects(self):
        return self._file_objects

    @file_objects.setter
    def file_objects(self, file_objects):
        self._file_objects = file_objects

    @property
    def supports_versions(self):
        """
        Does this repository support file versions?
        :return: (bool) True if versions supported, False if not.
        """
        return self._supports_versions


class S3FileObject(FileObject):
    MIN_BILLABLE_SIZE = 128 * 1024

    def __init__(self, object_summary):
        self._objectSummary = object_summary
        name = object_summary.object_key + '$' + object_summary.version_id
        size = object_summary.size
        if size is None:
            size = 0
        timestamp = object_summary.last_modified
        super().__init__(full_name=name, size=size, timestamp=timestamp)
        self._storage_class = S3StorageClass['STANDARD']
        self._billable_size = size

    @property
    def storage_class(self):
        return self._storage_class

    @property
    def billable_size(self):
        return self._billable_size


class LocalFileObject(FileObject):
    """
    File object for local hard drive or locally accessible file share
    """

    def __init__(self, full_name, path_delimiter='/'):
        size = os.path.getsize(full_name)
        timestamp = datetime.fromtimestamp(os.stat(full_name).st_mtime)
        super().__init__(size, timestamp, path_delimiter, full_name)


class S3Repository(Repository):
    def __init__(self, bucket_name):
        s3 = boto3.resource('s3')
        self._bucket = s3.Bucket(bucket_name)
        # versions = self._bucket.object_versions
        # for v in versions.all():
        #    print(v)
        # pull all objects from bucket and use to initialize base, versions supported
        super().__init__([S3FileObject(o) for o in self._bucket.object_versions.all()], supports_versions=True)


class LocalRepository(Repository):
    def __init__(self, root):
        files = self.get_files(root)
        super().__init__([LocalFileObject(name) for name in files], supports_versions=False)

    @staticmethod
    def get_files(root_folder):
        all_files = []
        for dir_path, dir_names, file_names in os.walk(root_folder):
            for filename in file_names:
                full_path = dir_path + os.sep + filename
                all_files.append(full_path)
        return all_files


class CachedRepository(Repository):
    def __init__(self, database_name):
        with sqlite3.connect(database_name) as db:
            cursor = db.cursor()
            cursor.execute('SELECT Name, Size, Time FROM FileObjects')
            done = False
            objects = []
            while not done:
                row = cursor.fetchone()
                if row is not None:
                    timestamp = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')
                    file_object = FileObject(full_name=row[0], size=row[1], timestamp=timestamp)
                    objects.append(file_object)
                else:
                    done = True
        super().__init__(objects)

    @classmethod
    def create_local_cached_database(cls, bucket_name, database_name=None):
        if not database_name:
            database_name = bucket_name + '.db'
        if os.path.exists(database_name):
            os.remove(database_name)
        bucket = S3Repository(bucket_name)
        with sqlite3.connect(database_name) as db:
            cursor = db.cursor()
            cursor.execute('''CREATE TABLE "FileObjects" ( 
                    "Name"	TEXT,
                    "Size"	INTEGER,
                    "Time"  TEXT
                    )''')
            for obj in bucket.file_objects:
                cursor.execute('''INSERT INTO FileObjects(Name,Size,Time)
                                      VALUES(?,?,?)''', (
                    obj.full_name, obj.size, obj.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')))
        return bucket

    @classmethod
    def load_from_cache(cls, bucket_name, database_name=None):
        if not database_name:
            database_name = bucket_name + '.db'
            bucket = CachedRepository(database_name)
            return bucket
