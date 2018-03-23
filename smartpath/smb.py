#! /usr/bin/python
# -*- coding: utf8 -*-
import smbclient

from .base import BaseClient, BasePath


class SambaClient(smbclient.SambaClient, BaseClient):
    '''Samba client for connecting to Windows/CIFS shares'''
    def __init__(self, **kwargs):
        BaseClient.__init__(self, uri=kwargs.pop('uri', 'smb://'), **kwargs)

        def resolve(x, default=None, action='pop'):
            f = getattr(kwargs, action)
            obj_default = getattr(self, x, default)
            return f(x, self.params[x] or self.query[x] or obj_default)

        # construct predictable smbclient defaults
        kws = dict([(k, resolve(k)) for k in
                    ('username', 'password', 'port', 'domain', 'resolve_order',
                     'ip', 'buffer_size', 'debug_level', 'config_file',
                     'logdir', 'netbios_name', 'workgroup')])

        smbclient.SambaClient(
            server=resolve('server') or resolve('hostname'),
            share=resolve('share') or self.getshare(),
            kerberos=resolve('kerberos', False),
            runcmd_attemps=resolve('runcmd_attemps', 1), **kws)

    def getshare(self):
        index = 1 if str(self.path)[0] is '/' else 0
        return getattr(self, 'share',
                       str(self.path).split('/')[index]
                       if self.path is not None else None)

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


class SambaPath(BasePath):
    '''Samba/Windows share path'''
    SESSION_FACTORY = SambaClient

    def __init__(self, uri, session=None, **kwargs):
        BasePath.__init__(self, uri, session, **kwargs)
        if not session:
            self.session = self.SESSION_FACTORY(uri=uri, **kwargs)
