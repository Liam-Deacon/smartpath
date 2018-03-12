#! /usr/bin/python
# -*- coding: utf8 -*-
'''
Utilities for handling different filesystems
'''
import os
import re
import pathlib

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def uriparse(uri):
    return urlparse(uri)


class SessionError(object):
    pass


class UriPath(object):
    def __init__(self, uri, session=None):
        '''
        Initialise UriPath with optional attached session
        session must be an object with the following method signatures:
            - cwd (may be property rather than method)
            - exists(path)
            - listdir(path)
            - mkdir(path, mode, parents, exist_ok)
            - rmdir(path)
            - stat(path)
            - open(path, *args, **kwargs)

        '''
        self.uri = uri
        uri = uriparse(uri)

        self.scheme = uri.scheme
        self.hostname = uri.hostname
        self.port = uri.port
        self.path = uri.path
        self.query = uri.query

        self.username = uri.username
        self.password = uri.password

        self.session = session

    def __str__(self):
        return self.uri

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.uri))

    def __div__(self, other):
        return self.__class__(self.uri.replace(self.path,
                              self.path + '/' + str(other)))

    def __add__(self, other):
        new_path = self.path + '/' + str(getattr(other, 'path', other))
        return self.__class__(self.uri.replace(self.path, new_path))

    @property
    def anchor(self):
        '''The concatenation of the drive and root, or ''.'''
        raise NotImplementedError

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

    def chmod(self):
        '''Change the permissions of the path, like os.chmod().'''
        raise NotImplementedError('Not supported on {} filesystem'
                                  ''.format(self.scheme))

    def cwd(self):
        '''Return a new path pointing to the current working directory
        as given by remote session or None if not supported.'''
        cwd = self.session.cwd
        cwd = cwd() if callable(cwd) else cwd
        return self.__class__(self.uri.replace(self.path, cwd))

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
        return self.__class__(self.uri.replace(self.path, new_path))

    def glob(self, pattern):
        '''Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given pattern.'''
        return (self.__class__(self.uri.replace(self.path, p))
                for p in self.session.listdir(self.path)
                if re.match(pattern.replace('*', '.*'), self.path))

    def group(self):
        '''Return the group name of the file gid.'''
        return gid_to_group_func(self.gid)

    def suffix(self):
        '''The final component's last suffix, if any.'''
        return os.path.splitext(self.path)[1]

    def home(self):
        '''Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).'''
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
        return (p for p in self.session.listdir(self.path)
                if self.session.is_dir(p))

    def joinpath(self, *args):
        '''Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).'''
        new_path = self.path + '/' + '/'.join(args)
        return self.__class__(self.uri.replace(self.path, new_path))

    def lchmod(self, mode):
        '''Like chmod(), except if the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.'''
        raise NotImplementedError

    def lstat(self):
        '''Like stat(), except if the path points to a symlink, the symlink's
        status information is returned, rather than its target's.'''
        raise NotImplementedError

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
        raise NotImplementedError

    @property
    def parent(self):
        '''The logical parent of the path.'''
        new_path = os.path.dirname(self.path)
        return self.__class__(self.uri.replace(self.path, new_path))

    @property
    def parents(self):
        path = self.path
        while path != '/':
            path = os.path.dirname(path)
            yield self.__class__(self.uri.replace(self.path, path))

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

    def relative_to(self, *other):
        '''Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        a subpath of the other path), raise ValueError.'''
        raise NotImplementedError

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
        return self.__class__(self.uri.replace(self.path, '/'.join(parts)))

    def rmdir(self):
        '''Remove this directory.  The directory must be empty.'''
        self.session.rmdir(self.path)

    @property
    def root(self):
        '''The root of the path, if any.'''
        return '/'

    def samefile(self, other):
        '''Return whether other_path is the same or not as this file'''
        raise NotImplementedError

    def stat(self):
        '''Return the result of the stat() system call on this path, like
        os.stat() does.'''
        return self.session.stat(self.path)

    def suffixes(self):
        '''A list of the final component's suffixes, if any.'''
        return ['.' + seg for seg in self.name.split('.')[1:]]

    def symlink_to(target, target_is_directory=False):
        '''Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) is the reverse
        of os.symlink's.'''
        raise NotImplementedError

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
        return self.__class__(self.uri.replace(self.path, new_path))

    def with_suffix(self, suffix):
        '''Return a new path with the file suffix changed
        (or added, if none).'''
        if not suffix.startswith('.'):
            ValueError('Invalid suffix {}'.format(repr(suffix)))
        new_path = os.path.splitext(self.path)[0] + suffix
        return self.__class__(self.uri.replace(self.path, new_path))

    def write_bytes(self, data):
        '''Open the file in bytes mode, write to it, and close the file.'''
        with self.session.open(self.path, 'wb') as f:
            f.write(data)

    def write_text(self, text):
        '''Open the file in text mode, write to it, and close the file.'''
        with self.session.open(self.path, 'w') as f:
            f.write(text)
