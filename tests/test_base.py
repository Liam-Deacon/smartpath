import unittest

import pathlib
import shutil
import os

from smartpath.base import BaseClient, BasePath

uri = 'https://test:pass@localhost:63197/{path}?testing=true&stuff=hello%20world&a=null'
local_uri = 'file://{path}'


class TestBaseClient(unittest.TestCase):
    def test_BaseClient___init__(self):
        '''Test BaseClient()'''
        bc = BaseClient(uri.format(path='path'))
        self.assertEqual(bc.username, 'test')
        self.assertEqual(bc.password, 'pass')
        self.assertEqual(bc.hostname, 'localhost')
        self.assertEqual(bc.port, 63197)
        self.assertEqual(bc.path, 'path')
        self.assertEqual(bc.netloc, 'test:pass@localhost:63197')
        self.assertEqual(bc.query, 'testing=true&stuff=hello%20world&a=null')
        self.assertEqual(bc.testing, True)
        self.assertEqual(bc.stuff, 'hello world')
        self.assertEqual(bc.a, None)

        bc = BaseClient(uri.format(path='path') + '&path=/to/somewhere/else',
                        testing=False, path='alternative/path')
        self.assertEqual(bc.testing, False)
        self.assertEqual(bc.path, 'alternative/path')
        self.assertEqual(getattr(bc, 'path_', None), '/to/somewhere/else')

    def test_BaseClient_newpath(self):
        '''Test BaseClient.newpath()'''
        bc = BaseClient(uri.format(path='path'))
        self.assertEqual(bc.getpath(), BasePath(uri.format(path='path')))

        self.assertEqual(bc.getpath('alternative/path'),
                         BasePath(uri.format(path='alternative/path')))

    def test_BaseClient_stat(self):
        '''Test BaseClient.stat()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').stat('path')

    def test_BaseClient_lstat(self):
        '''Test BaseClient.lstat()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').lstat('path')

    def test_BaseClient_open(self):
        '''Test BaseClient.open()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('').open('path')

    def test_BaseClient_listdir(self):
        '''Test BaseClient.listdir()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').listdir('path')

    def test_BaseClient_scandir(self):
        '''Test BaseClient.scandir()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').scandir()

    def test_BaseClient_chmod(self):
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').chmod('path', 0o777)

    def test_BaseClient_lchmod(self):
        '''Test BaseClient.lchmod()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').lchmod('path', 0o777)

    def test_BaseClient_rename(self):
        '''Test BaseClient.rename()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').rename()

    def test_BaseClient_symlink(self):
        '''Test BaseClient.symlink()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').symlink()

    def test_BaseClient_utime(self):
        '''Test BaseClient.utime()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').utime()

    def test_BaseClient_readlink(self):
        '''Test BaseClient.readlink()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').readlink()

    def test_BaseClient_unlink(self):
        '''Test BaseClient.unline()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').unlink()

    def test_BaseClient_replace(self):
        '''Test BaseClient.replace()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').replace()

    def test_BaseClient_mkdir(self):
        '''Test BaseClient.mkdir()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').mkdir()

    def test_BaseClient_makedirs(self):
        '''Test BaseClient.makedirs()'''
        with self.assertRaises(NotImplementedError):
            BaseClient('https://localhost').makedirs()


class TestBasePath(unittest.TestCase):
    class DummyClient(BaseClient):
        SESSION_FACTORY = pathlib.PosixPath

    def test_BasePath___init__(self):
        '''Test BasePath()'''
        bc = BasePath('', session=self.DummyClient)
        self.assertIsInstance(bc, BasePath)

    def test_BasePath_with_block(self):
        '''Test with BasePath() block'''
        with BasePath(local_uri) as bc:
            self.assertIsInstance(bc, BasePath)

    def test_BasePath_query(self):
        '''Test BasePath.query property'''
        bp = BasePath('file://to/some/thing?query=True')

    def test_BasePath_anchor_property(self):
        '''Test BasePath.anchor property'''
        self.assertEqual(BasePath(local_uri).anchor, '.')

    def test_BasePath_absolute(self):
        '''Test BasePath.absolute()'''
        self.assertEqual(BasePath(local_uri).absolute(),
                         BasePath(local_uri))

    def test_BasePath_as_posix(self):
        '''Test BasePath.as_posix()'''
        self.assertEqual(BasePath(local_uri).as_posix(),
                         BasePath(local_uri))

    def test_BasePath_as_uri(self):
        '''Test BasePath.as_uri()'''
        self.assertEqual(BasePath(local_uri).as_uri(), local_uri)

    def test_BasePath_chmod(self):
        '''Test BasePath.chmod()'''
        self.fail('todo')

    def test_BasePath_cwd(self):
        '''Test BasePath.cwd()'''
        self.fail('todo')

    def test_BasePath_drive_property(self):
        '''Test BasePath.drive property'''
        self.fail('todo')

    def test_BasePath_exists(self):
        '''Test BasePath.exists()'''
        self.fail('todo')

    def test_BasePath_expanduser(self):
        '''Test BasePath.expanduser()'''
        self.assertEqual(BasePath(local_uri).expanduser())

    def test_BasePath_glob(self):
        '''Test BasePath.glob()'''
        self.fail('todo')

    def test_BasePath_group(self):
        '''Test BasePath.group()'''
        self.assertEqual(BasePath(local_uri), None)

    def test_BasePath_suffix(self):
        self.fail('todo')

    def test_BasePath_home(self):
        '''Test BasePath.home()'''
        self.assertEqual(BasePath.home(), os.path.expanduser('~'))

    def test_BasePath_is_absolute(self):
        '''Test BasePath.is_absolute()'''
        self.assertEqual(BasePath(local_uri).is_absolute(), True)

    def test_BasePath_is_block_device(self):
        '''Test BasePath.is_block_device()'''
        self.assertEqual(BasePath(local_uri).is_block_device(), False)

    def test_BasePath_is_char_device(self):
        '''Test BasePath.is_char_device()'''
        self.assertEqual(BasePath(local_uri).is_char_device(), False)

    def test_BasePath_is_dir(self):
        '''Test BasePath.is_dir()'''
        self.assertEqual(BasePath(local_uri).is_absolute(), True)

    def test_BasePath_is_fifo(self):
        '''Test BasePath.is_fifo()'''
        self.assertEqual(BasePath(local_uri).is_fifo(), False)

    def test_BasePath_is_reserved(self):
        '''Test BasePath.is_reserved()'''
        self.assertEqual(BasePath(local_uri).is_reserved(), False)

    def test_BasePath_is_socket(self):
        '''Test BasePath.is_socket()'''
        self.assertEqual(BasePath(local_uri).is_socket(), False)

    def test_BasePath_is_symlink(self):
        '''Test BasePath.is_symlink()'''
        self.assertEqual(BasePath(local_uri).is_symlink(), False)

    def test_BasePath_iterdir(self):
        self.fail('todo')

    def test_BasePath_joinpath(self):
        self.fail('todo')

    def test_BasePath_lchmod(self):
        with self.assertRaises(NotImplementedError):
            self.fail('todo')

    def test_BasePath_lstat(self):
        with self.assertRaises(NotImplementedError):
            self.fail('todo')

    def test_BasePath_match(self):
        self.fail('todo')

    def test_BasePath_mkdir(self):
        self.fail('todo')

    def test_BasePath_name(self):
        self.fail('todo')

    def test_BasePath_open(self):
        self.fail('todo')

    def test_BasePath_owner(self):
        self.assertEqual(BasePath(local_uri).owner(), None)

    def test_BasePath_parent_property(self):
        self.fail('todo')

    def test_BasePath_parents_property(self):
        self.fail('todo')

    def test_BasePath_parts_property(self):
        self.fail('todo')

    def test_BasePath_read_bytes(self):
        self.fail('todo')

    def test_BasePath_read_text(self):
        self.fail('todo')

    def test_BasePath_replace(self):
        self.fail('todo')

    def test_BasePath_test_BasePath_relative_to(self):
        self.fail('todo')

    def test_BasePath_rename(self):
        self.fail('todo')

    def test_BasePath_resolve(self):
        self.fail('todo')

    def test_BasePath_rmdir(self):
        self.fail('todo')

    def test_BasePath_rmtree(self):
        self.fail('todo')

    def test_BasePath_root_property(self):
        self.assertTrue(BasePath(local_uri).root, '/')

    def samefile(self):
        self.assertTrue(BasePath(local_uri).samefile(local_uri))

    def test_BasePath_stat(self):
        self.fail('todo')

    def test_BasePath_suffixes(self):
        self.fail('todo')

    def test_BasePath_symlink_to(self):
        with self.assertRaises(NotImplementedError):
            self.fail('todo')

    def test_BasePath_touch(self):
        self.fail('todo')

    def test_BasePath_unlink(self):
        self.fail('todo')

    def test_BasePath_with_name(self):
        self.fail('todo')

    def test_BasePath_with_suffix(self):
        self.fail('todo')

    def test_BasePath_write_bytes(self):
        self.fail('todo')

    def test_BasePath_write_text(self):
        self.fail('todo')
