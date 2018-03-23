import unittest
from smartpath.nfs import NFSClient, NFSPath


class TestNFSClient(unittest.TestCase):
    def test_NFSClient(self):
        '''Test NFSClient()'''
        nfs = NFSClient('nfs://hello')
        #self.assertTrue(hasattr(nfs, '__init_dict'))
        self.assertTrue(hasattr(nfs, 'username'))
        self.assertTrue(hasattr(nfs, 'password'))
        self.assertTrue(hasattr(nfs, 'hostname'))
        self.assertTrue(hasattr(nfs, 'netloc'))

    def test_NFSClient_getpath(self):
        nfs = NFSClient('nfs://share')
        self.assertIsInstance(nfs.getpath('/to/somewhere'), NFSPath)


class TestNFSPath(unittest.TestCase):
    def test_NFSPath(self):
        '''Test NFSPath()'''
        self.fail('todo')
