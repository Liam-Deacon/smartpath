#! /usr/bin/python
# -*- coding: utf8 -*-
import smbclient

from .base import BaseClient, BasePath


class SmbClient(smbclient.SambaClient, BaseClient):
    def rmtree(self, path):
        return self.rmdir(path)

    def replace(self, src, dst):
        return self.rename(src, dst)

    def makedirs(self, path):
        raise NotImplementedError('TODO')

    def is_dir(self, path):
        return self.isdir(path)

    def scandir(self, path):
        return (p for p in self.listdir(path))


class SmbPath(BasePath):
    SESSION_FACTORY = smbclient.SambaClient

    def __init__(self, uri, session=None):
        super(BaseClient, self).__init__(uri, session)
        if not self.session:
            try:
                self.session = self.SESSION_FACTORY(self.hostname,
                                                    self.path.split('/')[0],
                                                    username=self.username,
                                                    password=self.password)
            except Exception:
                pass
