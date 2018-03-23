import os
import re

from abc import ABCMeta
from contextlib import contextmanager
from io import BytesIO, StringIO

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

try:
    import pathlib
    from pathlib import _Accessor
except ImportError:
    pathlib = None
    _Accessor = object


class SessionError(object):
    pass


class NamedBytesIO(BytesIO):
    '''Allows BytesIO instance to be named'''
    def __init__(self, initial_bytes=b'', name=None):
        super(BytesIO, self).__init__(initial_bytes)
        self.name = name

    def __str__(self):
        return self.name or super(BytesIO, self).__str__()


class NamedStringIO(StringIO):
    '''Allows StringIO instance to be named'''
    def __init__(self, initial_value='', name=None):
        super(StringIO, self).__init__(initial_value)
        self.name = name

    def __str__(self):
        return self.name or super(StringIO, self).__str__()


def not_implemented(func):
    '''Wrapper for functions without implementations,
    but unlink `abstractmethod`, are not required for class'''
    def wrapper(*args, **kwargs):
        raise NotImplementedError('{}() not available'.format(func.__name__))
    return wrapper


class BasePath(object):
    SESSION_FACTORY = pathlib.PosixPath

    def __init__(self, uri=None, session=None, **kwargs):
        '''
        Initialise BasesPath with optional attached session
        session must be an object with the following method signatures:
            - cwd (may be property rather than method)
            - exists(path)
            - listdir(path)
            - mkdir(path, mode, parents, exist_ok)
            - rmdir(path)
            - stat(path)
            - open(path, *args, **kwargs)

        '''
        self.uri = uri or ''
        uri = urlparse(uri or 'file://')

        self.scheme = self._drv = uri.scheme  # _drv for compatibility with pathlib
        self.netloc = self._root = uri.netloc  # _root for compatibility with pathlib
        self.hostname = uri.hostname or kwargs.get('hostname', kwargs.get('server'))
        self.port = uri.port or None
        self.path = uri.path or None
        self.query = uri.query or None

        self.username = uri.username or None
        self.password = uri.password or None

        self.session = session

        uri_dict = dict([(k, getattr(uri, k, None)) for k in
                         ('scheme', 'netloc', 'hostname', 'port', 'path', 'query')])
        kwargs.update(dict([(k, v) for k, v in uri_dict.items() if uri_dict[k]]))
        self._init_dict_ = kwargs
        try:
            if self.session is None and callable(self.SESSION_FACTORY):
                try:
                    self.session = self.SESSION_FACTORY(**kwargs)
                except ValueError:
                    # remove unwanted entries
                    kw = dict([(k, v) for (k, v) in kwargs.items() if k not in
                               ('scheme', 'netloc', 'path', 'query')])
                    self.session = self.SESSION_FACTORY(**kw)
            elif self.session is None and not callable(self.SESSION_FACTORY):
                self.session = self.SESSION_FACTORY
        except Exception:
            pass

    def __str__(self):
        return self.uri

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.uri))

    def __div__(self, other):
        return self.__class__(self.uri.replace(self.path,
                              self.path + '/' + str(other)))

    def __add__(self, other):
        new_path = self.path + '/' + str(getattr(other, 'path', other))
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    def __eq__(self, other):
        return str(self) == str(other)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @property
    def session(self):
        return getattr(self, '_session', None)

    @session.setter
    def session(self, new_session):
        if not hasattr(self, '_accessor'):
            self._accessor = None
        if new_session is not None:
            self._session = self._accessor = new_session

    @property
    def query(self):
        return parse_qs(self._query)

    @query.setter
    def query(self, query_string):
        self._query = query_string

    @property
    def anchor(self):
        '''The concatenation of the drive and root, or ''.'''
        return '.'

    def absolute(self):
        '''Return an absolute version of this path.
        On Remote filesystems this is the same as path.'''
        return self

    def as_posix(self):
        '''Return the string representation of the path with
        forward (/) slashes.'''
        return self.path

    def as_uri(self):
        '''Return the path as a URI.'''
        return self.uri

    def chmod(self, mode):
        '''Change the permissions of the path, like os.chmod().'''
        self.session.chmod(self.path, mode)

    def cwd(self):
        '''Return a new path pointing to the current working directory
        as given by remote session or None if not supported.'''
        cwd = self.session.cwd
        cwd = cwd() if callable(cwd) else cwd
        return self.__class__(self.uri.replace(self.path, cwd),
                              session=self.session)

    @property
    def drive(self):
        '''The drive prefix (letter or UNC path), if any.'''
        return ''

    def exists(self):
        '''Whether this path exists.'''
        return self.session.exists(self.path)

    def expanduser(self):
        '''Return a new path with expanded ~ and ~user constructs
        (as returned by os.path.expanduser)'''
        new_path = os.path.expanduser(self.path)
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    def glob(self, pattern):
        '''Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given pattern.'''
        return (self.__class__(self.uri.replace(self.path, p), self.session)
                for p in self.session.listdir(self.path)
                if re.match(pattern.replace('*', '.*'), self.path))

    def group(self):
        '''Return the group name of the file gid or `None`.'''
        return None

    def suffix(self):
        '''The final component's last suffix, if any.'''
        return os.path.splitext(self.path)[1]

    @classmethod
    def home(cls):
        '''Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).'''
        import pathlib
        return pathlib.Path.home()

    def is_absolute(self):
        '''Always true as URL paths start at root of share'''
        return True

    def is_block_device(self):
        '''Whether this path is a block device.'''
        return self.session.is_block_device(self.path)

    def is_char_device(self):
        '''Whether this path is a character device.'''
        return self.session.is_char_device(self.path)

    def is_dir(self):
        return self.session.is_dir(self.path)

    def is_fifo(self):
        '''Whether this path is a FIFO.'''
        return self.session.is_fifo(self.path)

    def is_reserved(self):
        '''Return True if the path contains one of the special names reserved
        by the system, if any.'''
        return self.session.is_reserved(self.path)

    def is_socket(self):
        return self.session.is_socket(self.path)

    def is_symlink(self):
        return self.session.is_symlink(self.path)

    def iterdir(self):
        '''Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.'''
        if self.session.is_dir(self.path):
            return (p for p in self.session.listdir(self.path)
                    if p not in ['.', '..'])
        raise SessionError('{} is not a directory'.format(repr(self.path)))

    def joinpath(self, *args):
        '''Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).'''
        new_path = self.path + '/' + '/'.join(args)
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    @not_implemented
    def lchmod(self, mode):
        '''Like chmod(), except if the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.'''
        pass

    @not_implemented
    def lstat(self):
        '''Like stat(), except if the path points to a symlink, the symlink's
        status information is returned, rather than its target's.'''
        pass

    def match(self, pattern):
        '''Return True if this path matches the given pattern.'''
        return bool(re.match(pattern.replace('*', '.*'), self.path))

    def mkdir(self, mode=511, parents=False, exist_ok=False):
        '''Create a new directory at this given path.'''
        return self.session.mkdir(self.path, mode, parents, exist_ok)

    @property
    def name(self):
        '''Returns the basename of path'''
        return os.path.basename(self.path)

    def open(self, *args, **kwargs):
        '''Open the file pointed by this path and return a file object, as
        the built-in open() function does.'''
        return self.session.open(self.path, *args, **kwargs)

    def owner(self):
        '''Return the login name of the file owner.'''
        return None

    @property
    def parent(self):
        '''The logical parent of the path.'''
        new_path = os.path.dirname(self.path)
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    @property
    def parents(self):
        path = self.path
        while path != '/':
            path = os.path.dirname(path)
            yield self.__class__(self.uri.replace(self.path, path),
                                 session=self.session)

    @property
    def parts(self):
        '''An object providing sequence-like access to the
        components in the filesystem path.'''
        return [p or '/' for p in self.path.split('/')]

    def read_bytes(self):
        '''Open the file in bytes mode, read it, and close the file.'''
        with self.session.open(self.path, 'rb') as f:
            _bytes = f.read()
        return _bytes

    def read_text(self):
        '''Open the file in text mode, read it, and close the file.'''
        with self.session.open(self.path, 'r') as f:
            text = f.read()
        return text

    def replace(self, target):
        '''Rename this path to the given path, clobbering the existing
        destination if it exists.'''
        new_uri = self.uri.replace(self.path, target)
        self.__class__(new_uri).write_bytes(self.read_bytes())
        self.unlink()

    @not_implemented
    def relative_to(self, *other):
        '''Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        a subpath of the other path), raise ValueError.'''
        pass

    def rename(self, target):
        '''Rename this path to the given path.'''
        self.replace(target)

    def resolve(self):
        '''Make the path absolute, resolving all symlinks on the way and also
        normalizing it (for example turning slashes into backslashes under
        Windows).
        '''
        parts = [self.path.replace('/./', '/').split('/')]
        while True:
            try:
                index = parts.index('..')
                parts.pop(index)
                parts.pop(index - 1)
            except ValueError:
                break
        return self.__class__(self.uri.replace(self.path, '/'.join(parts)),
                              session=self.session)

    def rmdir(self):
        '''Remove this directory.  The directory must be empty.'''
        self.session.rmdir(self.path)

    def rmtree(self):
        '''Remove entire directory tree.'''
        return self.session.rmtree(self.path)

    @property
    def root(self):
        '''The root of the path, if any.'''
        return '/'

    @not_implemented
    def samefile(self, other):
        '''Return whether other_path is the same or not as this file'''
        pass

    def stat(self):
        '''Return the result of the stat() system call on this path, like
        os.stat() does.'''
        return self.session.stat(self.path)

    def suffixes(self):
        '''A list of the final component's suffixes, if any.'''
        return ['.' + seg for seg in self.name.split('.')[1:]]

    @not_implemented
    def symlink_to(target, target_is_directory=False):
        '''Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) is the reverse
        of os.symlink's.'''
        pass

    def touch(self, mode=438, exist_ok=True):
        '''Create this file with the given access mode, if it doesn't exist.'''
        return self.session.open(self.path, 'wb')

    def unlink(self):
        '''Remove this file or link.
        If the path is a directory, use rmdir() instead.'''
        return self.session.unlink(self.path)

    def with_name(self, name):
        '''Return a new path with the file name changed.'''
        new_path = self.path.replace(self.name, name)
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    def with_suffix(self, suffix):
        '''Return a new path with the file suffix changed
        (or added, if none).'''
        if not suffix.startswith('.'):
            ValueError('Invalid suffix {}'.format(repr(suffix)))
        new_path = os.path.splitext(self.path)[0] + suffix
        return self.__class__(self.uri.replace(self.path, new_path),
                              session=self.session)

    def write_bytes(self, data):
        '''Open the file in bytes mode, write to it, and close the file.'''
        with self.session.open(self.path, 'wb') as f:
            f.write(data)

    def write_text(self, text):
        '''Open the file in text mode, write to it, and close the file.'''
        with self.session.open(self.path, 'w') as f:
            f.write(text)


class BaseClient(_Accessor):
    '''A base client to act as a mixin'''
    __metaclass__ = ABCMeta
    __pathclass__ = BasePath

    def __init__(self, uri, **kwargs):
        # initialise object dictionary with kwargs
        self.__dict__.update(kwargs)

        # add uri and update class dictionary if missing keys
        self.uri = uri
        self._uri = uri = urlparse(uri)
        self.username = getattr(self, 'username', uri.username)
        self.password = getattr(self, 'password', uri.password)
        self.hostname = getattr(self, 'hostname', uri.hostname or '127.0.0.1')
        self.netloc = getattr(self, 'netloc', uri.netloc)  # TODO: bug possible here due to hostname fix above
        self.port = getattr(self, 'port', uri.port)
        self.path = getattr(self, 'path', uri.path[1:] or os.path.abspath('.'))
        self.fragment = getattr(self, 'fragment', uri.fragment)
        self.scheme = getattr(self, 'scheme', uri.scheme or 'https')
        self.params = getattr(self, 'params', uri.params)
        self.query = getattr(self, 'query', uri.query)

        def naive_convert(t):
            try:
                s = str(t)
                if s.lower() == 'true':
                    s = True
                elif s.lower() == 'false':
                    s = False
                elif s.lower() in ['null', 'none']:
                    s = None
                return eval(str(s))
            except Exception:
                return t

        # add query items to class dictionary, avoiding name clashes
        self.__dict__.update(dict([(key, naive_convert(val[0]))
                             if key not in self.__dict__
                             else ('{}_'.format(key), naive_convert(val[0]))
                             for (key, val) in parse_qs(uri.query).items()]))

    def getpath(self, path=None):
        '''Returns associated Path type for client'''
        uri = self.uri.replace(self._uri.path, '/' + (path or self.path))
        return self.__pathclass__(uri, self)

    @not_implemented
    def stat(self, path):
        pass

    @not_implemented
    def lstat(self, path):
        pass

    @not_implemented
    @contextmanager
    def open(self, path, mode='r'):
        yield open(path, mode)

    @not_implemented
    def listdir(self, path=''):
        pass

    @not_implemented
    def scandir(self, *args):
        pass

    @not_implemented
    def chmod(self, path, mode):
        pass

    @not_implemented
    def lchmod(self, pathobj, mode):
        pass

    @not_implemented
    def rename(self, src, dst):
        pass

    @not_implemented
    def symlink(a, b, target_is_directory):
        pass

    @not_implemented
    def utime(self, path, times=None, *, ns=None,
              dir_fd=None, follow_symlinks=True):
        pass

    # Helper for resolve()
    @not_implemented
    def readlink(self, path):
        pass

    # alias functions for uniform interface
    @not_implemented
    def unlink(self, path):
        pass

    @not_implemented
    def replace(self, path, new_path):
        pass

    @not_implemented
    def mkdir(self, path, **kwargs):
        pass

    @not_implemented
    def makedirs(self, path, **kwargs):
        pass
