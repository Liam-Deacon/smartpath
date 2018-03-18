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
        bp = BasePath('file://to/some/thing?query=True')
        bp

    def test_BasePath_anchor_property(self):
        self.fail('todo')

    def test_BasePath_absolute(self):
        self.fail('todo')

    def test_BasePath_as_posix(self):
        self.fail('todo')

    def test_BasePath_as_uri(self):
        self.fail('todo')

    def test_BasePath_chmod(self):
        self.fail('todo')

    def test_BasePath_cwd(self):
        self.fail('todo')

    def test_BasePath_drive_proerty(self):
        self.fail('todo')

    def test_BasePath_exists(self):
        self.fail('todo')

    def test_BasePath_expanduser(self):
        self.fail('todo')

    def test_BasePath_glob(self):
        self.fail('todo')

    def test_BasePath_group(self):
        self.fail('todo')

    def test_BasePath_suffix(self):
        self.fail('todo')

    def test_BasePath_home(self):
        self.fail('todo')

    def test_BasePath_is_absolute(self):
        self.fail('todo')

    def test_BasePath_is_block_device(self):
        self.fail('todo')

    def test_BasePath_is_char_device(self):
        self.fail('todo')

    def test_BasePath_is_dir(self):
        self.fail('todo')

    def test_BasePath_is_fifo(self):
        self.fail('todo')

    def test_BasePath_is_reserved(self):
        self.fail('todo')

    def test_BasePath_is_socket(self):
        self.fail('todo')

    def test_BasePath_is_symlink(self):
        self.fail('todo')

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
        self.fail('todo')

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
        self.fail('todo')

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
