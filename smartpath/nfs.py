'''Module for handling NFS paths'''
import libnfs

from .base import BasePath, BaseClient

import datetime


class NFSClient(libnfs.NFS, BaseClient):
    def __init__(self, uri=None, **kwargs):
        BaseClient.__init__(self, uri or 'nfs://', **kwargs)
        libnfs.NFS.__init__(self, uri)


class NFSPath(BasePath):
    '''A Network File Share Path'''
    SESSION_FACTORY = NFSClient

    def __init__(self, uri, session=None, **kwargs):
        BasePath.__init__(uri, session, **kwargs)
        if not session:
            self.session = self.SESSION_FACTORY(uri, **kwargs)

    def is_file(self):
        return self.session.isfile(self.path)

    def is_dir(self):
        return self.session.isdir(self.path)

    @property
    def modified_time(self):
        return datetime.datetime.fromtimestamp(
            self.session.stat(self.path)['mtime']['sec'])

    @property
    def created_time(self):
        return datetime.datetime.fromtimestamp(
            self.session.stat(self.path)['mtime']['sec'])


NFSClient.__pathclass__ = NFSPath
