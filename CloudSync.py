from Util.Repository import Repository
from enum import Enum

class OperationType(Enum):
    '''
    Enumeration of operation types
    '''
    Update = 1
    Replicate = 2
    Synchronize = 3
    Restore = 4

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
    parser.add_argument('--source', help='Source', required=True)
    parser.add_argument('--target', help='Target', required=True)
    parser.add_argument('--op', help='Operation type', required=True)

    args = parser.parse_args()

    opType = args.op
    operation_type = OperationType[opType]
    print(f'{operation_type.Description}: {args.source} -> {args.target}')

