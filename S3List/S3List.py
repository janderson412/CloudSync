import os
from Util.Repository import CachedRepository

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
        bucket = CachedRepository.create_local_cached_database(bucketName)
    else:
        bucket = CachedRepository.load_from_cache(bucketName)

    allNames = ['/' + o.full_name for o in bucket.file_objects]

    for name in allNames:
        print(name)

