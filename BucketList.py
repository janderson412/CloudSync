from enum import Enum
import boto3
from openpyxl import Workbook
from Util.S3Repository import Repository, FileObject, FileVersion

class OutputType(Enum):
    StandardOutput = 1
    TextFile = 2
    Excel = 3


class BucketOutput:
    def __init__(self, output_type, output_header, show_versions, filename=None):
        self._type = output_type
        self._filename = filename
        self._output_header = output_header
        self._show_versions = show_versions

    @property
    def type(self):
        return self._type

    @property
    def filename(self):
        return self._filename

    @property
    def output_header(self):
        return self._output_header

    @property
    def show_versions(self):
        return self._show_versions


def output_file_objects(repository, output):
    items = list()
    if output.show_versions:
        header = 'key,version_id,time_stamp,size,deleted,num_versions'
        for key, o in repository.file_objects.items():
            line = f'{key},,{o.time_stamp},{o.size},{o.is_deleted},{o.num_versions}'
            items.append(line)
            for v in sorted(o.versions, reverse=True):
                line = f',{v.version_id},{v.time_stamp},{v.size},{v.is_delete_marker},'
                items.append(line)
    else:
        header = 'key,time_stamp,size,deleted'
        for o in repository.file_objects:
            line = f'{o.key},{o.time_stamp},{o.size},{o.is_deleted}'
            items.append(line)
    if output.type == OutputType.StandardOutput:
        if output.output_header:
            print(header)
        for o in items:
            print(o)

    if output.type == OutputType.TextFile:
        with open(output.filename, mode='w') as f:
            if output.output_header:
                f.write(header + '\n')
            for o in items:
                f.write(o)

    if output.type == OutputType.Excel:
        wb = Workbook()
        ws = wb.active
        if output.output_header:
            header_items = header.split(sep=',')
            for n in range(len(header_items)):
                ws.cell(column=n + 1, row=1, value=header_items[n])
        row = 2
        for o in items:
            col = 1
            line_items = o.split(sep=',')
            for x in line_items:
                ws.cell(row=row, column=col, value=x)
                col += 1
            row += 1
        wb.save(output.filename)

def get_file_object_output(o, output):
    if output.show_versions:
        return f'{o.key},{o.id},{o.is_latest},{o.size},{o.last_modified},{o.storage_class},{o.version_id}'
    else:
        return f'{o.key},{o.id},{o.is_latest},{o.size},{o.last_modified},{o.storage_class},{o.version_id}'


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='S3 Bucket List')
    parser.add_argument('bucket', help='Bucket name', metavar='bucket-name')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', help='Output file for delimited text output', metavar='text-file')
    output_group.add_argument('-e', help='Excel file for output', metavar='Excel-file')
    parser.add_argument('--header', help='Output header line', action='store_true')
    parser.add_argument('--versions', help='Output information about all versions', action='store_true')
    args = parser.parse_args()

    bucket_output = None
    if args.o:
        bucket_output = BucketOutput(OutputType.TextFile, args.header, args.versions, filename=args.o)
    elif args.e:
        bucket_output = BucketOutput(OutputType.Excel, args.header, args.versions, filename=args.e)
    else:
        bucket_output = BucketOutput(OutputType.StandardOutput, args.header, args.versions)

    # s3 = boto3.resource('s3')
    # selected_bucket = s3.Bucket(args.bucket)
    # output_file_objects(selected_bucket, bucket_output)

    repository = Repository(args.bucket)
    output_file_objects(repository, bucket_output)
