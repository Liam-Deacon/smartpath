import os
import unittest

from smartpath.smb import SmbClient, SmbPath


SHARE = os.environ.get('SMARTPATH_SAMBA_TEST_SHARE')
SmbClient()


class TestSmbClient(unittest.TestCase):
    def test_SmbClient(self):
        '''Test SmbClient()'''
        raise NotImplementedError


class TestSmbPath(unittest.TestCase):
    def test_SmbPath(self):
        '''Test SmbPath()'''
        raise NotImplementedError

