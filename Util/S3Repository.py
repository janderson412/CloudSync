
import boto3


class FileObject:
    def __init__(self, key, bucket_object=None, bucket_object_version=None):
        if not bucket_object and not bucket_object_version:
            raise Exception('Must supply either bucket_object or bucket_object_version')
        elif bucket_object and bucket_object_version:
            raise Exception('Can\'t use both bucket_object and bucket_object_version')
        self._key = key
        self._versions = list()
        self._num_versions = 0
        if bucket_object_version is not None:
            file_version = FileVersion(bucket_object_version)
            self.add_version(file_version)
        else:
            self._time_stamp = bucket_object.last_modified
            self._size = bucket_object.size
            self._is_deleted = False
            self._num_versions = 1

    def add_version(self, file_version):
        self._versions.append(file_version)
        if file_version.is_latest:
            self._time_stamp = file_version.time_stamp
            self._size = file_version.size
            self._is_deleted = file_version.is_delete_marker
        self._num_versions += 1

    @property
    def key(self):
        return self._key

    @property
    def versions(self):
        return self._versions

    @property
    def time_stamp(self):
        return self._time_stamp

    @property
    def size(self):
        return self._size

    @property
    def is_deleted(self):
        return self._is_deleted

    @property
    def num_versions(self):
        return self._num_versions


class FileVersion:
    def __init__(self, o):
        self._version_id = o.id
        self._time_stamp = o.last_modified
        self._size = o.size
        self._is_latest = o.is_latest

    @property
    def version_id(self):
        return self._version_id

    @property
    def time_stamp(self):
        return self._time_stamp

    @property
    def size(self):
        if self._size:
            return self._size
        else:
            return 0

    @property
    def is_latest(self):
        return self._is_latest

    @property
    def is_delete_marker(self):
        if self._size is None:
            return True
        else:
            return False

    def __cmp__(self, other):
        if self._time_stamp < other.time_stamp:
            return -1
        elif self._time_stamp > other.time_stamp:
            return 1
        return 0

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __le__(self, other):
        return self.time_stamp <= other.time_stamp

    def __gt__(self, other):
        return self.time_stamp > other.time_stamp

    def __ge__(self, other):
        return self.time_stamp >= other.time_stamp


class Repository:
    def __init__(self, bucket_name):
        client = boto3.client('s3')
        response = client.get_bucket_versioning(Bucket=bucket_name)
        if 'Status' in response and response['Status'] == 'Enabled':
            self._versioning = True
        else:
            self._versioning = False
        s3 = boto3.resource('s3')
        self._bucket = s3.Bucket(bucket_name)
        self._objects = dict()
        if self._versioning:
            objects = self._bucket.object_versions.all()
            for o in objects:
                if o.key in self._objects:
                    self._objects[o.key].add_version(FileVersion(o))
                else:
                    self._objects[o.key] = FileObject(o.key, bucket_object_version=o)
        else:
            objects = self._bucket.objects.all()
            for o in objects:
                self._objects[o.key] = FileObject(o.key, bucket_object=o)

    @property
    def file_objects(self):
        return self._objects

    @property
    def versioning(self):
        return self._versioning
