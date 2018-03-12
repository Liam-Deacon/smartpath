import ftplib
import ftputil
import pysftp

from .base import BaseClient, BasePath


class FTPTLSSession(ftplib.FTP_TLS):
    '''FTP session factory with TLS support'''
    def __init__(self, host, user, password, port=21):
        super(ftplib.FTP_TLS, self).__init__(self)
        self.connect(host, port)
        self.login(user, password)
        self.prot_p()  # set the encrypted data connection


class FTPClient(BaseClient):
    def __init__(self, uri, session=None):
        super(BaseClient, self).__init__(uri, session)
        self._factory = ftplib.FTP
        if self.scheme == 'ftps':
            self._factory = FTPTLSSession
        self.session = self.session or (
            ftputil.FTPHost(self.hostname, self.username, self.password,
                            session_factory=self._factory))


class SFTPClient(pysftp.Connection):
    def __init__(self, **kwargs):
        super(pysftp.Connection, self).__init__(**kwargs)
