from azure.storage.blob import BlockBlobService
from azure.storage.file import FileService
from contextlib import contextmanager
from functools import partial

import os

from .base import (BaseClient, BasePath,
                   NamedBytesIO, NamedStringIO)


class AzureStorageBaseClient(BaseClient):
    ENV_PREFIX = 'AZURE_'
    _factory = None

    def __init__(self, host, port=0, auth=None,
                 username=None, password=None, use_env=True):
        if use_env:
            username = username or os.environ.get(self.ENV_PREFIX + 'USERNAME')
            password = password or os.environ.get(self.ENV_PREFIX + 'PASSWORD')
            auth = auth or os.environ.get(self.ENV_PREFIX + 'AUTH')
        self._service = self._factory(account_name=username,
                                      account_key=password)

    @staticmethod
    def _splitAzurePath(path):
        if not path:
            raise ValueError('Container/Share must be specified in URI - '
                             'so cannot handle empty paths')
        container = path.split(path[1:] if path.startswith('/') else path, '/')
        return container[0], '/'.join(container[1:])

    @property
    def containers(self):
        return (c.name for c in
                getattr(self._service, 'list_containers',
                        getattr(self._service, 'list_shares'))())


class AzureFileStorageClient(AzureStorageBaseClient):
    ENV_PREFIX = 'AZURE_FILE_'
    _factory = FileService

    def exists(self, path):
        share, subpath = self._splitAzurePath(path)
        exists = partial(self._service.exists, share)
        return (exists(subpath) or
                exists(os.path.dirname(subpath), os.path.basename(subpath)))

    def read_bytes(self, path):
        container, subpath = self._splitAzurePath(path)
        return self._service.get_blob_to_bytes(container, subpath).content

    def read_text(self, path):
        container, subpath = self._splitAzurePath(path)
        return self._service.get_blob_to_text(container, subpath).content

    def write_bytes(self, path, _bytes):
        container, subpath = self._splitAzurePath(path)
        return self._service.create_file_from_bytes(container,
                                                    os.path.dirname(subpath),
                                                    os.path.basename(subpath),
                                                    _bytes)

    def write_text(self, path, text):
        container, subpath = self._splitAzurePath(path)
        return self._service.create_file_from_text(container,
                                                   os.path.dirname(subpath),
                                                   os.path.basename(subpath),
                                                   text)

    @contextmanager
    def open(self, path, mode='r'):
        container, subpath = self._splitAzurePath(path)
        if mode == 'r':
            _file = self._service.get_file_to_text(container,
                                                   os.dirname(subpath),
                                                   os.basename(subpath))
            stream = NamedStringIO(_file.content, name=_file.name)
        elif mode == 'rb':
            _file = self._service.get_file_to_bytes(container,
                                                    os.dirname(subpath),
                                                    os.basename(subpath))
            stream = NamedBytesIO(_file.content, name=_file.name)
        elif mode == 'w':
            stream = NamedStringIO(name=subpath)
        elif mode == 'wb':
            stream = NamedBytesIO(name=subpath)
        else:
            raise NotImplementedError(mode + ' is not supported')
        try:
            yield stream
        finally:
            if mode == 'w':
                file_write = self._service.create_file_from_text
            elif mode == 'wb':
                file_write = self._service.create_file_from_bytes
            else:
                return
            self.makedirs(os.dirname(path))
            file_write(container, os.path.dirname(subpath),
                       os.path.basename(subpath), stream.getvalue())

    def is_dir(self, path):
        try:
            self._service.get_directory_metadata(*self._splitAzurePath(path))
            return True
        except Exception:
            return False

    def listdir(self, path=''):
        return list(self.scandir(path))

    def scandir(self, *args):
        container, subpath = self._splitAzurePath('/'.join(args))
        files = self._service.list_directories_and_files(container, subpath)
        return (f.name for f in files)

    def rename(self, src, dst):
        src_container, src_name = self._splitAzurePath(src)
        src_file_url = self._service.make_file_url(src_container,
                                                   os.path.dirname(src_name),
                                                   os.path.basename(src_name))
        dst_container, dst = self._splitAzurePath(dst)
        c = self._service.copy_file(dst_container, os.path.dirname(dst),
                                    os.path.basename(dst), src_file_url)
        self._service.delete_file(src_container, os.path.dirname(src_name),
                                  os.path.basename(src_name))
        return c

    def replace(self, path, new_path):
        return self.rename(path, new_path)

    def rmdir(self, path, **kwargs):
        return self.delete_directory(*self._splitAzurePath(path))

    def rmtree(self, path, **kwargs):
        return self.rmdir(path)

    def mkdir(self, path, **kwargs):
        share, subpath = self._splitAzurePath(path)
        if share not in self.containers:
            self._service.create_share(share)
        dirs = subpath.split('/')
        for i in range(1, len(dirs)):
            self._service.create_directory(share, '/'.join(dirs[:i]))

    def makedirs(self, path, **kwargs):
        return self.mkdir(path, **kwargs)

    def unlink(self, path):
        share, subpath = self._splitAzurePath(path)
        if not subpath:
            if not self.scandir(path):
                # only delete when share is empty
                return self._service.delete_share(share)
            raise PermissionError('Share not empty & no file or dir to delete')
        if self.is_dir(path):
            self._service.delete_directory(share, subpath)
        else:
            self._service.delete_blob(share, subpath)


class AzureBlobStorageClient(AzureStorageBaseClient):
    ENV_PREFIX = 'AZURE_BLOB_'
    _factory = BlockBlobService

    def exists(self, path):
        container, subpath = self._splitAzurePath(path)
        exists = self._service.exists(container, subpath)
        return exists or bool(self.listdir(path))

    def read_bytes(self, path):
        container, subpath = self._splitAzurePath(path)
        return self._service.get_blob_to_bytes(container, subpath).content

    def read_text(self, path):
        container, subpath = self._splitAzurePath(path)
        return self._service.get_blob_to_text(container, subpath).content

    def write_bytes(self, path, bytes):
        container, blobpath = self._splitAzurePath(path)
        self._service.create_blob_from_bytes(container, blobpath, bytes)

    def write_text(self, path, text):
        container, subpath = self._splitAzurePath(path)
        self._service.create_blob_from_text(container, subpath, text)

    @contextmanager
    def open(self, path, mode='r'):
        container, subpath = self._splitAzurePath(path)
        if mode == 'r':
            blob = self._service.get_blob_to_text(container, subpath)
            stream = NamedStringIO(blob.content, name=blob.name)
        elif mode == 'rb':
            blob = self._service.get_blob_to_bytes(container, subpath)
            stream = NamedBytesIO(blob.content, name=blob.name)
        elif mode in ['w', 'wb']:
            named_io_class = NamedBytesIO if mode is 'wb' else NamedStringIO
            stream = named_io_class(name=subpath)
        else:
            raise NotImplementedError(mode + ' is not supported')
        try:
            yield stream
        finally:
            if mode == 'w':
                blob_write = self._service.create_blob_from_text
            elif mode == 'wb':
                blob_write = self._service.create_blob_from_bytes
            else:
                return
            self._service.create_container(container, fail_if_exist=False)
            blob_write(container, subpath, stream.getvalue())

    def listdir(self, path=''):
        return list(self.scandir(path))

    def scandir(self, *args):
        container, subpath = self._splitAzurePath('/'.join(args))
        blobs = self._service.list_blobs(container)
        return (blob.name for blob in blobs if blob.name.startswith(subpath))

    def rename(self, src, dst):
        src_container, src_blob_name = self._splitAzurePath(src)
        src_blob_url = self._service.make_blob_url(src_container,
                                                   src_blob_name)

        dst_container, dst_blob_name = self._splitAzurePath(dst)
        c = self._service.copy_blob(dst_container, dst_blob_name, src_blob_url)
        self._service.delete_blob(src_container, src_blob_name)
        return c

    def rmdir(self, dirpath):
        pass

    def rmtree(self, dirpath):
        dirs = self.listdir(dirpath)
        for d in dirs:
            self.unlink(d)
        return dirs

    def replace(self, path, new_path):
        return self.rename(path, new_path)

    def mkdir(self, path, **kwargs):
        pass  # not needed => doesn't do anything

    def makedirs(self, path, **kwargs):
        pass  # not needed => doesn't do anything

    def unlink(self, path):
        container, blobpath = self._splitAzurePath(path)
        if blobpath:
            self._service.delete_blob(container, blobpath)
        elif len(self.scandir(path)):
            raise PermissionError('Blob container not empty')


class AzurePath(BasePath):
    @property
    def anchor(self):
        '''The concatenation of the drive and root, or ''.'''
        return self.session._splitAzurePath(self.path)[0]

    def cwd(self):
        '''Return a new path pointing to the current working directory
        as given by remote session or None if not supported.'''
        return None

    def open(self, *args, **kwargs):
        '''Open the file pointed by this path and return a file object, as
        the built-in open() function does.'''
        return self.session.open(self.path, *args, **kwargs)

    def read_bytes(self):
        '''Open the file in bytes mode, read it, and close the file.'''
        return self.session.read_bytes(self.path)

    def read_text(self):
        '''Open the file in text mode, read it, and close the file.'''
        return self.session.read_text(self.path)

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
        raise ValueError('Not Supported')

    def rename(self, target):
        '''Rename this path to the given path.'''
        self.replace(target)

    def rmdir(self):
        '''Remove this directory.  The directory must be empty.'''
        self.session.rmdir(self.path)

    @property
    def root(self):
        '''The root of the path, if any.'''
        return '/'

    def samefile(self, other):
        '''Return whether other_path is the same or not as this file'''
        return self.uri == getattr(other, 'uri', None)

    def suffixes(self):
        '''A list of the final component's suffixes, if any.'''
        return ['.' + seg for seg in self.name.split('.')[1:]]

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
        return self.session.write_bytes(self.path, data)

    def write_text(self, text):
        '''Open the file in text mode, write to it, and close the file.'''
        return self.session.write_text(self.path, text)
