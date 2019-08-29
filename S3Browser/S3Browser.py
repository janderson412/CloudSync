import wx, os, boto3, time
import sys
import sqlite3
from Util.Repository import CachedRepository, S3Repository, S3FileObject, LocalRepository

class ObjectListPanel(wx.Panel):
    def __init__(self, parent):
        '''

        Args:
            parent:
        '''
        super().__init__(parent)
        self.horizontal = wx.BoxSizer(wx.HORIZONTAL)
        self.RowObjDict = {}

        self._listControl = wx.ListCtrl(
            self, size=(-1,-1),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.EXPAND
        )
        self._listControl.InsertColumn(0, 'Key', width=140)
        self._listControl.InsertColumn(1, 'Size', width=40)
        self._listControl.InsertColumn(2, 'Timestamp', width=80)
        self._listControl.InsertColumn(3, 'Class', width=80)
        self._listControl.InsertColumn(4, 'BillableSize', width=80)

        #self.horizontal.Add(self.ListControl, 0, wx.ALL | wx.EXPAND, 10)
        self.horizontal.Add(self._listControl, proportion=1, flag=wx.EXPAND)

        self.vertical = wx.BoxSizer(wx.VERTICAL)
        self.vertical.Add(self.horizontal, proportion=1, flag=wx.EXPAND)

        self._label = wx.StaticText(self, label='Label here')
        self.vertical.Add(self._label)

        self.SetSizerAndFit(self.vertical)

class ObjectListFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None,
                         title='S3 Object Browser')
        self.panel = ObjectListPanel(self)
        self.Show()

    @property
    def ListControl(self):
        return self.panel._listControl

    @property
    def Label(self):
        return self.panel._label

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='S3 object browser')
    parser.add_argument('--bucket', help='Name of bucket browse')
    parser.add_argument('--folder', help='Name of folder to browse')
    parser.add_argument('--refresh', action='store_true', default=False, help='Refresh local cached database from S3 storage')
    args = parser.parse_args()

    repository = None
    if args.bucket:
        bucketName = args.bucket
        dbName = bucketName + '.db'
        if (not os.path.exists(dbName)) or args.refresh:
            repository = CachedRepository.create_local_cached_database(bucketName)
        else:
            repository = CachedRepository.load_from_cache(bucketName)

    elif args.folder:
        folder = args.folder
        repository = LocalRepository(folder)

    else:
        parser.print_help()
        sys.exit(1)

    app = wx.App(False)
    frame = ObjectListFrame()

    index = 0
    totalSize = 0
    for fileObj in repository.file_objects:
        if type(fileObj) is S3FileObject:
            frame.ListControl.Append([fileObj.full_name, fileObj.size, fileObj.timestamp.isoformat(), fileObj.storage_class.name, fileObj.billable_size])
        else:
            frame.ListControl.Append([fileObj.full_name, fileObj.size, fileObj.timestamp.isoformat()])
        totalSize += fileObj.size
        index = index + 1
    totalSizeInMb = totalSize / (1024 * 1024)
    frame.Label.SetLabel(f'Total size: {totalSize:,} ({totalSizeInMb:.2f} MB)')

    app.MainLoop()