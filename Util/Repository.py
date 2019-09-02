import os
import boto3
import time
from enum import Enum
import sqlite3
from datetime import datetime


class S3StorageClass(Enum):
    '''
    Enumeration of Amazon S3 storage types.
    '''
    STANDARD = 1
    REDUCED_REDUNDANCY = 2
    GLACIER = 3
    STANDARD_IA = 4
    ONEZONE_IA = 5
    INTELLIGENT_TIERING = 6
    DEEP_ARCHIVE = 7


class FileObject:
    '''
    A FileObject contains information about a single object stored in the cloud.  This is an abstract class
    that is realized with an Amazon S3 file object or filesystem file object.
    '''
    def __init__(self, size=0, timestamp = datetime.now(), path_delimiter = '/', full_name = None, name = None, folder = None):
        '''

        :param size: (long) Size of file object in bytes (default: 0)
        :param timestamp: (datetime) Timestamp of file object (default: current time)
        :param path_delimiter: (string) delimiter for components of file path (default: '/'
        :param full_name: (string) Full name of file object, including path (relative to root of repository)
        :param name: (string) Name of file object (without path)
        :param folder: (string) Folder containing file object
        '''
        if full_name == None and (name == None or folder == None):
            raise Exception('Full path not given and either name or folder missing')
        if full_name != None and (name != None or folder != None):
            raise Exception('Full name given and either name or folder are defined')
        if size < 0:
            raise Exception('Size must be greater than or equal to 0')
        if full_name != None:
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
        '''
        Get the name of the object, without the full path.

        :returns: (string) Name of object (key)
        '''
        return self._name

    @property
    def full_name(self):
        '''
        Get the full pathname of the file object.

        :return: (string) Full pathname of file object.
        '''
        return self._full_name

    @property
    def folder(self):
        return self._folder

    @property
    def size(self):
        '''
        Get the size of the object.

        :return: (int) Size of object, in bytes
        '''
        return self._size

    @property
    def timestamp(self):
        '''
        Get the date & time object was stored.

        :return: (datetime) Date/time when object stored.
        '''
        return self._timestamp

class Repository():
    '''
    A repository for holding FileObjects.
    '''
    def __init__(self, fileObjects, supports_versions = False):
        '''
        
        :param fileObjects: 
        '''
        self._file_objects = fileObjects
        self._supports_versions = supports_versions

    @property
    def file_objects(self):
        return self._file_objects

    @file_objects.setter
    def file_objects(self, file_objects):
        self._file_objects = file_objects

    @property
    def supports_versions(self):
        '''
        Does this repository support file versions?
        :return: (bool) True if versions supported, False if not.
        '''
        return self._supports_versions


class S3FileObject(FileObject):
    MIN_BILLABLE_SIZE = 128 * 1024

    def __init__(self, objectSummary):
        self._objectSummary = objectSummary
        name = objectSummary.object_key + '$' + objectSummary.version_id
        size = objectSummary.size
        if size is None:
            size = 0
        timestamp = objectSummary.last_modified
        super().__init__(full_name=name, size=size, timestamp=timestamp)
        self._storage_class = S3StorageClass['STANDARD']
        self._billable_size = size
        #self._storage_class = S3StorageClass[objectSummary.storage_class]

        #if (self._storage_class == S3StorageClass.STANDARD_IA or self._storage_class == S3StorageClass.ONEZONE_IA) and \
                #size < S3FileObject.MIN_BILLABLE_SIZE:
            #self._billable_size = S3FileObject.MIN_BILLABLE_SIZE
        #else:
            #self._billable_size = size

    @property
    def storage_class(self):
        return self._storage_class

    @property
    def billable_size(self):
        return self._billable_size

class LocalFileObject(FileObject):
    '''
    File object for local hard drive or locally accessible file share
    '''
    def __init__(self, full_name, path_delimiter = '/'):
        size = os.path.getsize(full_name)
        timestamp = datetime.fromtimestamp(os.stat(full_name).st_mtime)
        super().__init__(size, timestamp, path_delimiter, full_name)


class S3Repository(Repository):
    def __init__(self, bucketName):
        s3 = boto3.resource('s3')
        self._bucket = s3.Bucket(bucketName)
        #versions = self._bucket.object_versions
        #for v in versions.all():
        #    print(v)
        # pull all objects from bucket and use to initialize base, versions supported
        super().__init__([S3FileObject(o) for o in self._bucket.object_versions.all()], supports_versions=True)


class LocalRepository(Repository):
    def __init__(self, root, filter=None):
        files = self.get_files(root)
        super().__init__([LocalFileObject(name) for name in files], supports_versions=False)

    @staticmethod
    def get_files(root_folder):
        allFiles = []
        for dirpath, dirnames, filenames in os.walk(root_folder):
            for filename in filenames:
                fullpath = dirpath + os.sep + filename
                allFiles.append(fullpath)
        return allFiles

class CachedRepository(Repository):
    def __init__(self, dbName):
        with sqlite3.connect(dbName) as db:
            cursor = db.cursor()
            cursor.execute('SELECT Name, Size, Time FROM FileObjects')
            done = False
            objects = []
            while not done:
                row = cursor.fetchone()
                if row != None:
                    #fileObject = FileObject(row[0], row[1], time.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'), row[3], S3StorageClass(row[4]))
                    timestamp=datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')
                    fileObject = FileObject(full_name=row[0], size=row[1], timestamp=timestamp)
                    objects.append(fileObject)
                else:
                    done = True
        super().__init__(objects)

    @classmethod
    def create_local_cached_database(cls, bucketName, dbName=None):
        if not dbName:
            dbName = bucketName + '.db'
        if os.path.exists(dbName):
            os.remove(dbName)
        bucket = S3Repository(bucketName)
        with sqlite3.connect(dbName) as db:
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
    def load_from_cache(cls, bucketName, dbName=None):
        if not dbName:
            dbName = bucketName + '.db'
            bucket = CachedRepository(dbName)
            return bucket

