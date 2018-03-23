import os
import unittest

from smartpath.smb import SambaClient, SambaPath


SHARE = os.environ.get('SMARTPATH_SAMBA_TEST_SHARE')


class TestSmbClient(unittest.TestCase):
    def test_SambaClient(self):
        '''Test SambaClient()'''
        SambaClient()


class TestSmbPath(unittest.TestCase):
    def test_SambaPath(self):
        '''Test SambaPath()'''
        SambaPath()

