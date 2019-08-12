import os
from S3Util.Bucket import CachedBucket

def CreateFolderHierrarchy(allNames, dict, root):
    for name in allNames:


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='S3 Object Lister')
    parser.add_argument('--bucket', help='Name of bucket browse')
    parser.add_argument('--refresh', action='store_true', default=False,
                        help='Refresh local cached database from S3 storage')
    args = parser.parse_args()

    bucketName = args.bucket
    dbName = bucketName + '.db'
    bucket = None
    if (not os.path.exists(dbName)) or args.refresh:
        bucket = CachedBucket.CreateLocalCachedDatabase(bucketName)
    else:
        bucket = CachedBucket.LoadFromCache(bucketName)

    allNames = ['/' + o.Name for o in bucket.BucketObjects]

    for name in allNames:
        print(name)

    dict = dict()
    root = '/'
    CreateFolderHierrarchy(allNames, dict, root)
