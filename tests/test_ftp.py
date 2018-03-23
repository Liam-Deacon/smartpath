import os
import unittest
import random

from smartpath.ftp import FTPClient, FTPPath

from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler, DummyAuthorizer
from threading import Thread

FTP_PORT = random.randint(49152, 65534)
FTP_SERVER = FTPServer
FTP_SERVER_THREAD = None
FTP_USER = 'testuser'
FTP_PASSWORD = 'testing123'


def setUpModule():
    global FTP_SERVER, FTP_SERVER_THREAD
    auth = DummyAuthorizer()
    auth.add_user(FTP_USER, FTP_PASSWORD, '.', perm="elradfmwMT")
    handler = FTPHandler
    handler.authorizer = auth
    FTP_SERVER = FTPServer(('localhost', FTP_PORT), handler)
    FTP_SERVER_THREAD = Thread(target=FTP_SERVER.serve_forever,
                               daemon=True, args=(2, False))
    FTP_SERVER_THREAD.run()


def setTearDownModule():
    FTP_SERVER_THREAD.join()
    FTP_SERVER.close_all()


class TestFtpClient(unittest.TestCase):
    def test_FTPClient(self):
        print(FTP_PORT)
        FTPClient()


class TestFTPPath(unittest.TestCase):
    def test_FTPPath(self):
        self.fail('TODO')