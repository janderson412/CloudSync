from Util.Repository import Repository
from enum import Enum
import sys

class OperationType(Enum):
    '''
    Enumeration of operation types
    '''
    Update = 1
    Replicate = 2
    Synchronize = 3
    Restore = 4
    ListOnly = 5

    @property
    def Description(self):
        if self == OperationType.Update:
            return 'Update target'
        elif self == OperationType.Replicate:
            return 'Replicate source to target'
        elif self == OperationType.Synchronize:
            return 'Synchronize source and target'
        elif self == OperationType.Restore:
            return 'Restore source from target'
        elif self == OperationType.ListOnly:
            return 'List objects in target'


'''
Command line:
CloudSync --source <src> --target <trg> --op {Update | Replicate | Synchronize | Restore}

Where:
  <src> is full pathname of root of source directory
  <trg> is target, either "dir:<directory>" or "s3:<bucketname>"
'''
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Syncrhonize between local folder and file server or S3 bucket')
    parser.add_argument('--source', help='Source', required=False)
    parser.add_argument('--target', help='Target', required=True)
    parser.add_argument('--op', help='Operation type (one of: Update, Replicate, Synchronize, Restore or ListOnly', required=True)
    parser.add_argument('--showonly', help='No changes, only show chnages that would be made', required=False)
    parser.add_argument('--refresh', help='Refresh local database for remote repository (S3 only)')

    args = parser.parse_args()
    opType = args.op
    operation_type = OperationType[opType]
    if operation_type != OperationType.ListOnly and args.source == None:
        print('Must specify source with --source if operation is other than ListOnly')
        parser.print_help()
        sys.exit(1)

    print(f'{operation_type.Description}: {args.source} -> {args.target}')

'''
s3.list_object_versions(
    Bucket='jea-scratch',
    Prefix='<key>'

'''
