'''Module for handling WebDAV paths'''
import easywebdav

import dateutil
import time
import os

import tempfile

from .base import BasePath


class WebDavClient(easywebdav.Client):
    '''WebDAV client providing os-like functions'''

    def __init__(self, host, port=0, auth=None,
                 username=None, password=None, protocol=None,
                 verify_ssl=True, path=None, cert=None, use_env=True):
        if use_env:
            username = username or os.environ.get('WEBDAV_USERNAME')
            password = password or os.environ.get('WEBDAV_PASSWORD')
            auth = auth or os.environ.get('WEBDAV_AUTH')
            port = port or os.environ.get('WEBDAV_SERVER_PORT')
            protocol = protocol or os.environ.get('WEBDAV_SERVER_PROTOCOL',
                                                  'https')
            verify_ssl = os.environ.get('WEBDAV_VERIFY_SSL', verify_ssl)
            path = path or os.environ.get('WEBDAV_PATH')
            cert = cert or os.environ.get('WEBDAV_CERT')
        kwargs = dict([(key, val) for key, val in locals().items() if key in
                       ('host', 'username', 'password', 'auth', 'port',
                        'protocol', 'verify_ssl', 'path', 'cert')])
        super(easywebdav.Client, self).__init__(**kwargs)

    def stat(self, path):
        return stat_result(self.ls(path)[0])

    def lstat(self, path):
        raise NotImplementedError

    def open(self, path, mode='r'):
        if 'r' in mode:
            pass
        elif 'w' in mode:
            os.path.split(path)[0]
        else:
            raise ValueError('Unsupported mode: {}'.format(repr(mode)))

    def listdir(self, path=''):
        [f.name for f in self.ls(path)]

    def scandir(self, *args):
        raise (f.name for f in self.ls('/' + '/'.join(args)))

    def utime(self, path, times=None, *, ns=None,
              dir_fd=None, follow_symlinks=True):
        raise NotImplementedError

    def rename(self, src, dst):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.download(src, os.path.join(tmpdir, 'temp'))
            self.upload(os.path.join(tmpdir, 'temp'), dst)

    # alias functions for uniform interface
    unlink = easywebdav.Client.delete
    replace = rename
    makedirs = easywebdav.Client.mkdirs


class stat_result(object):
    def __init__(self, path):
        self._file = path

    @property
    def st_mode(self):
        raise NotImplementedError

    @property
    def st_ino(self):
        '''return inode number'''
        raise NotImplementedError

    @property
    def st_dev(self):
        '''return device'''
        raise NotImplementedError

    @property
    def st_nlink(self):
        '''return number of hard links'''
        raise NotImplementedError

    @property
    def st_uid(self):
        '''return user id of owner'''
        raise NotImplementedError

    @property
    def st_gid(self):
        '''return group id of owner'''
        raise NotImplementedError

    @property
    def st_size(self):
        '''return size of file, in bytes'''
        return self._file.size

    @property
    def st_atime(self):
        '''time of most recent access'''
        atime = dateutil.parser.parse(self.mtime)
        return round(time.mktime(atime.timetuple()))

    @property
    def st_mtime(self):
        '''return time of most recent content modification'''
        mtime = dateutil.parser.parse(self.mtime)
        return round(time.mktime(mtime.timetuple()))

    @property
    def st_ctime(self):
        '''return time of most recent metadata change'''
        ctime = dateutil.parser.parse(self.ctime)
        return round(time.mktime(ctime.timetuple()))


class WebDavPath(easywebdav.File, BasePath):
    SESSION_FACTORY = WebDavClient

    def __init__(self, uri, session=None, **kwargs):
        BasePath.__init__(self, uri, session, **kwargs)
        if not self.session:
            self.SESSION_FACTORY(
                host=self.hostname,
                port=self.port or 0,
                auth=None,
                username=self.username or kwargs.get('username'),
                password=self.password or kwargs.get('password'),
                protocol=kwargs.pop('protocol', self.query.get('protocol')),
                verify_ssl=kwargs.pop('verify_ssl',
                                      self.query.get('verify_ssl', True)),
                path=kwargs.get('path') or self.path,
                cert=kwargs.get('cert', self.query.get('cert')),
                use_env=kwargs.get('use_env', self.query.get('use_env', True))
            )
        try:
            self.stat = self.session.stat(self.path)
            self.__dict__.update(self.stat._asdict())
            easywebdav.File(self.path, *self.stat._asdict().values())
        except easywebdav.client.OperationFailed:
            easywebdav.File(self.path, None, None, None, None)  # defer to later

    @property
    def modified_time(self):
        return getattr(self, 'mtime', None)

    @property
    def created_time(self):
        return getattr(self, 'ctime', None)

    @property
    def anchor(self):
        '''The concatenation of the host and root, or ''.'''
        return '{}/'.format(self.hostname)

    @property
    def stem(self):
        return os.path.splitext(os.path.basename(self.path))[0]
