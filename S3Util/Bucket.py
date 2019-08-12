import wx, os, boto3, time
from enum import Enum
import sqlite3

class StorageClass(Enum):
    STANDARD = 1
    REDUCED_REDUNDANCY = 2
    GLACIER = 3
    STANDARD_IA = 4
    ONEZONE_IA = 5
    INTELLIGENT_TIERING = 6
    DEEP_ARCHIVE = 7

class FileObject():
    def __init__(self, name, size, timestamp, billableSize, storageClass):
        self._name = name
        self._size = size
        self._timestamp = timestamp
        self._billableSize = billableSize
        self._storageClass = storageClass

    @property
    def Name(self):
        return self._name

    @property
    def Size(self):
        return self._size

    @property
    def Timestamp(self):
        return self._timestamp

    @property
    def BillableSize(self):
        return self._billableSize

    @property
    def StorageClass(self):
        return self._storageClass

class BucketObject(FileObject):
    MinBillableSize = 128 * 1024

    def __init__(self, objectSummary):
        self._objectSummary = objectSummary
        name = objectSummary._key
        size = objectSummary.size
        timestamp = objectSummary.last_modified
        storageClass = StorageClass[objectSummary.storage_class]
        if size < self.MinBillableSize and (storageClass == StorageClass.ONEZONE_IA or storageClass == StorageClass.STANDARD_IA):
            billableSize = self.MinBillableSize
        else:
            billableSize = size
        super().__init__(name, size, timestamp, billableSize, storageClass)

class Bucket():
    def __init__(self, bucketObjects):
        self._bucketObjects = bucketObjects

    @property
    def BucketObjects(self):
        return self._bucketObjects

class S3Bucket(Bucket):
    def __init__(self, bucketName):
        s3 = boto3.resource('s3')
        self._bucket = s3.Bucket(bucketName)
        super().__init__([BucketObject(o) for o in self._bucket.objects.all()])

class CachedBucket(Bucket):
    def __init__(self, dbName):
        with sqlite3.connect(dbName) as db:
            cursor = db.cursor()
            cursor.execute('SELECT Name, Size, Time, BillableSize, StorageClass FROM FileObjects')
            done = False
            objects = []
            while not done:
                row = cursor.fetchone()
                if row != None:
                    fileObject = FileObject(row[0], row[1], time.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'), row[3], StorageClass(row[4]))
                    objects.append(fileObject)
                else:
                    done = True
        super().__init__(objects)

    @classmethod
    def CreateLocalCachedDatabase(cls, bucketName, dbName=None):
        if not dbName:
            dbName = bucketName + '.db'
        if os.path.exists(dbName):
            os.remove(dbName)
        bucket = S3Bucket(bucketName)
        with sqlite3.connect(dbName) as db:
            cursor = db.cursor()
            cursor.execute('''CREATE TABLE "FileObjects" ( 
                    "Name"	TEXT,
                    "Size"	INTEGER,
                    "Time"  TEXT,
                    "BillableSize"	INTEGER,
                    "StorageClass"  INTEGER,
    	            PRIMARY KEY("Name")
                    )''')
            for obj in bucket.BucketObjects:
                cursor.execute('''INSERT INTO FileObjects(Name,Size,Time,BillableSize,StorageClass)
                                      VALUES(?,?,?,?,?)''', (
                    obj.Name, obj.Size, obj.Timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'), obj.BillableSize,
                    obj.StorageClass.value))
        return bucket

    @classmethod
    def LoadFromCache(cls, bucketName, dbName=None):
        if not dbName:
            dbName = bucketName + '.db'
            bucket = CachedBucket(dbName)
            return bucket

