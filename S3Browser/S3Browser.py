import wx, os, boto3, time
import sqlite3
from Bucket import CachedBucket, S3Bucket

class ObjectListPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.horizontal = wx.BoxSizer(wx.HORIZONTAL)
        self.RowObjDict = {}

        self.ListControl = wx.ListCtrl(
            self, size=(-1,-1),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.EXPAND
        )
        self.ListControl.InsertColumn(0, 'Key', width=140)
        self.ListControl.InsertColumn(1, 'Size', width=40)
        self.ListControl.InsertColumn(2, 'Class', width=80)

        #self.horizontal.Add(self.ListControl, 0, wx.ALL | wx.EXPAND, 10)
        self.horizontal.Add(self.ListControl, proportion=1, flag=wx.EXPAND)

        self.vertical = wx.BoxSizer(wx.VERTICAL)
        self.vertical.Add(self.horizontal, proportion=1, flag=wx.EXPAND)

        #self.SetSizer(mainSizer)
        self.SetSizerAndFit(self.vertical)

class ObjectListFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None,
                         title='S3 Object Browser')
        self.panel = ObjectListPanel(self)
        self.Show()

    @property
    def ListCtrl(self):
        return self.panel.ListControl

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='S3 object browser')
    parser.add_argument('--bucket', help='Name of bucket browse')
    parser.add_argument('--refresh', action='store_true', default=False, help='Refresh local cached database from S3 storage')
    args = parser.parse_args()

    bucketName = args.bucket
    dbName = bucketName + '.db'
    bucket = None
    if (not os.path.exists(dbName)) or args.refresh:
        bucket = CachedBucket.CreateLocalCachedDatabase(bucketName)
    else:
        bucket = CachedBucket.LoadFromCache(bucketName)

    app = wx.App(False)
    frame = ObjectListFrame()

    index = 0
    for fileObj in bucket.BucketObjects:
        frame.ListCtrl.Append([fileObj.Name, fileObj.Size, fileObj.StorageClass.name])
        index = index + 1

    app.MainLoop()