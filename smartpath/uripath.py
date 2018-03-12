#! /usr/bin/python
# -*- coding: utf8 -*-
'''Provides uniform interface for deciphering URI's
as though they are local files'''
import urllib.parse


class UriPath(object):
    def __init__(self, uri):
        self.uri = uri
        self.createSession()

    def createSession(self, **kwargs):
        '''Tries to create a new session appropriate to URI scheme'''
        scheme = self.scheme
        hostname = self.hostname
        if scheme is 'dav':
            from .dav import WebDavClient, WebDavPath
            self.session = WebDavClient(**kwargs)
            self.__class__ = WebDavPath
        elif scheme in ['ftp', 'ftps']:
            from .ftp import FTPClient, FTPSClient, FT
            client = FTPClient if scheme is 'ftp' else FTPSClient
            self.session = client(**kwargs)
        elif scheme is ['sftp']:
            raise NotImplementedError
        elif scheme is 'mogodb':
            from .mongodb import GridFsClient
            self.session = GridFsClient(**kwargs)
        elif scheme is 'nfs':
            from .nfs import NFSClient, NFSPath
            self.session = NFSClient(**kwargs)
            self.__class__ = NFSPath
        elif scheme in ['cifs', 'smb']:
            from .smb import SmbClient, SmbPath
            self.session = SmbClient(**kwargs)
            self.__class__ = SmbPath
        elif scheme in ['s3'] or hostname.endswith('s3.amazonaws.com'):
            from .s3 import S3Client, S3Path
            self.session = S3Client(**kwargs)
            self.__class__ = S3Path
        elif hostname.endswith('blob.core.windows.net'):
            from .azure import AzureBlobStorageClient
            self.session = AzureBlobStorageClient(**kwargs)
        elif hostname.endswith('file.core.windows.net'):
            from .azure import AzureFileStorageClient
            self.session = AzureFileStorageClient(**kwargs)
        try:
            # hack to change class
            self.__init__(self.uri, self.session)
        except TypeError:
            # didn't alter class of Path
            pass

    @classmethod
    def constructUri(cls, scheme='http', hostname='localhost', path='',
                     username=None, password=None, port=None,  **query_kwargs):
        '''Creates a URI from the given arguments'''
        schme = scheme.replace('://', '').lower()
        query = urllib.parse.urlencode(query_kwargs) if query_kwargs else ''
        auth = username if username else ''
        auth += ':{}'.format(password) if password else ''
        auth += '@' if auth else ''
        host = '{}:{}'.format(hostname, int(port)) if port else hostname
        return '{scheme}://{auth}{host}/{path}{query}'.format(**locals())
