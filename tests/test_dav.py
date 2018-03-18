import subprocess

import unittest

from smartpath.dav import WebDavClient, WebDavPath


class TestDavClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ps = subprocess.Popen(['wsgidav --host=0.0.0.0 --port=8080 --root=/tmp'], shell=True)
        cls.client = WebDavClient

    def test_webdavpath(self):
        WebDavPath()
