'''Module for handling FTP paths'''
import ftplib
import ftputil
import pysftp
import os

from .base import BaseClient, BasePath, NamedBytesIO, NamedStringIO

from contextlib import contextmanager


class FTPTLSSession(ftplib.FTP_TLS):
    '''FTP session factory with TLS support'''
    def __init__(self, host, user, password, port=21):
        super(ftplib.FTP_TLS, self).__init__(self)
        self.connect(host, port)
        self.login(user, password)
        self.prot_p()  # set the encrypted data connection


class FTPClient(ftputil.FTPHost, BaseClient):
    '''Simplified yet flexible FTP client'''
    def __init__(self, factory=ftplib.FTP, **kwargs):
        BaseClient.__init__(self, uri=kwargs.pop('uri', 'ftp://'), **kwargs)
        ftputil.FTPHost.__init__(
            self,
            kwargs.pop('server',
                       kwargs.pop('host',
                                  kwargs.pop('hostname',
                                             self.hostname))),
            kwargs.pop('username', self.username),
            kwargs.pop('password', self.password),
            port=kwargs.pop('port', self.port or 21),
            session_factory=factory, **kwargs)


class SFTPClient(pysftp.Connection, BaseClient):
    '''An FTP over SSH client'''
    def __init__(self, **kwargs):
        BaseClient.__init__(self, uri=kwargs.pop('uri', 'sftp://'), **kwargs)
        pysftp.Connection.__init__(
            self,
            kwargs.pop('server',
                       kwargs.pop('host',
                                  kwargs.pop('hostname',
                                             self.hostname))),
            username=kwargs.pop('username', self.username),
            private_key=kwargs.pop(
                'private_key', getattr(self, 'private_key',
                                       self.query.get('private_key'))),
            password=kwargs.pop('password', self.password),
            private_key_pass=kwargs.pop(
                'private_key_pass', getattr(self, 'private_key_pass',
                                            self.query.get('private_key_pass'))),
            port=kwargs.pop('port', self.port or 22),
            default_path=kwargs.pop(
                'default_path', self.path if len(self.path) > 1 else None),
            ciphers=kwargs.pop('ciphers', self.query.get('ciphers')),
            log=kwargs.pop('log', self.query.get('log', False)),
            cnopts=dict([(k, kwargs.get(k, self.query.get(k)))
                         for k in set(list(kwargs.keys()) +
                                      list(self.query.keys()))])
            )

    def is_dir(self, path):
        return self.isdir(path)

    @contextmanager
    def open(self, filename, mode='r', **kwargs):
        if '+' in mode or 'a' in mode:
            raise ValueError(mode + 'not supported')
        bio = NamedBytesIO(name='{}${}'.format(filename, str(self)))
        try:
            if mode.beginswith('r'):
                self.getfo(filename, bio)
                bio.seek(0)
            io = (bio if mode.endswith('b') else
                  NamedStringIO(bio.getvalue().decode('utf8')))
            yield io
        finally:
            if mode.beginswith('w'):
                if io != bio:
                    bio.write(io.getvalue().encode('ascii'))
                bio.seek(0)
                self.putfo(filename, bio)


class SFTPPath(BasePath):
    '''FTP over SSH path'''
    SESSION_FACTORY = SFTPClient

    def __init__(self, uri, session=None):
        super(BaseClient, self).__init__(uri, session)
        self.session = self.session or (
            SFTPClient(username=self.username,
                       password=self.password,
                       port=self.port or 22,
                       default_path=os.dirname(self.path),
                       private_key=self.query.get('private_key', None),
                       cnopts=self.query))


class FTPPath(BasePath):
    '''FTP or FTPS Path'''
    SESSION_FACTORY = FTPClient

    def __init__(self, uri, session=None, **kwargs):
        BasePath.__init__(self, uri, session, **kwargs)
        if self.scheme is 'sftp':
            self.session = session or SFTPClient(**kwargs)
            self.__class__ = SFTPPath  # dark magic to convert to SFTPPath
        else:
            factory = FTPTLSSession if self.scheme is 'ftps' else ftplib.FTP
            factory = kwargs.pop('session_factory', factory)
            self.session = session or (
                FTPClient(session_factory=factory, **kwargs))
