
from Util.Repository import FileObject
import pytest
from datetime import datetime

@pytest.fixture
def test_data():
    fmt = '%Y-%m-%d %H:%M:%S'
    t1 = datetime.strptime('2019-08-19 12:35:22', fmt)
    t2 = datetime.strptime('2019-06-30 06:30:00', fmt)
    t3 = datetime(2019, 8, 20)
    t4 = datetime(2003, 3, 26)
    data = [
        (FileObject(size=1000, timestamp=t1, full_name='/dir1/test1.txt'),
         1000, t1, '/dir1/test1.txt', '/dir1', 'test1.txt'),
        (FileObject(size=45281, timestamp=t2, name='test2.dat', folder='/dir1'),
         45281, t2, '/dir1/test2.dat', '/dir1', 'test2.dat'),
        (FileObject(size=23451, timestamp=t3, full_name='/dir1/config/a very long filename.txt'),
         23451, t3, '/dir1/config/a very long filename.txt', '/dir1/config', 'a very long filename.txt'),
        (FileObject(size=12, timestamp=t4, name='test3.dat', folder='/Windows/config/local'),
         12, t4, '/Windows/config/local/test3.dat', '/Windows/config/local', 'test3.dat'),
    ]
    return data

def test_properties(test_data):
    for data in test_data:
        f = data[0]
        assert isinstance(f, FileObject)
        assert f.size == data[1]
        assert f.timestamp == data[2]
        assert f.full_name == data[3]
        assert f.folder == data[4]
        assert f.name == data[5]

@pytest.fixture
def constructor_exception_args():
    '''
    Get arguments for constructor of FileObject that will fail
    :return: (dict) keyword arguments for constructor
    '''
    return [
        {'name' : 'file1.txt'},
        {'full_name' : '/dir1/dir2/test.dat', 'name' : 'test.dat'},
        {'full_name' : '/windows/config.txt', 'folder' : '/windows'},
        {'folder' : '/windows'},
        {'full_name' : '/etc/password', 'size' : -5}
    ]


def test_constructor_exceptions(constructor_exception_args):
    '''
    Construct FileObject and expect exception
    :param test_exception_args: (dict) Keyword arguments for constructor
    :return: (none)
    '''
    for case in constructor_exception_args:
        with pytest.raises(Exception):
            f = FileObject(**case)

