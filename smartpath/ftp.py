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


class FTPClient(ftputil.FTPHost):
    def __init__(self, factory=ftplib.FTP, **kwargs):
        super(ftputil.FTPHost, self).__init__(session_factory=factory,
                                              **kwargs)


class FTPPath(BasePath):
    SESSION_FACTORY = FTPClient

    def __init__(self, uri, session=None):
        super(BasePath, self).__init__(uri, session)
        factory = FTPTLSSession if self.scheme is 'ftps' else ftplib.FTP
        self.session = self.session or (
            FTPClient(self.hostname, self.username, self.password,
                      session_factory=factory))


class SFTPClient(pysftp.Connection):
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
    SESSION_FACTORY = pysftp.Connection

    def __init__(self, uri, session=None):
        super(BaseClient, self).__init__(uri, session)
        self.session = self.session or (
            SFTPClient(username=self.username,
                       password=self.password,
                       port=self.port or 22,
                       default_path=os.dirname(self.path),
                       private_key=self.query.get('private_key', None),
                       cnopts=self.query))
