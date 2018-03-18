import functools
import os
import sys

import gridfs
import pymongo

from pathlib import _Accessor
from .base import BasePath


class GridFsClient(object):
    class _NormalAccessor(_Accessor):
        pass

    def _wrap_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobj, *args):
            return strfunc(str(pathobj), *args)
        return staticmethod(wrapped)

    def _wrap_binary_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobjA, pathobjB, *args):
            return strfunc(str(pathobjA), str(pathobjB), *args)
        return staticmethod(wrapped)

    stat = _wrap_strfunc(os.stat)

    lstat = _wrap_strfunc(os.lstat)

    open = _wrap_strfunc(os.open)

    listdir = _wrap_strfunc(os.listdir)

    scandir = _wrap_strfunc(os.scandir)

    chmod = _wrap_strfunc(os.chmod)

    if hasattr(os, "lchmod"):
        lchmod = _wrap_strfunc(os.lchmod)
    else:
        def lchmod(self, pathobj, mode):
            raise NotImplementedError("lchmod() not available on this system")

    mkdir = _wrap_strfunc(os.mkdir)

    unlink = _wrap_strfunc(os.unlink)

    rmdir = _wrap_strfunc(os.rmdir)

    rename = _wrap_binary_strfunc(os.rename)

    replace = _wrap_binary_strfunc(os.replace)

    if sys.platform in ['nt', 'win32', 'win64']:
        if supports_symlinks:
            symlink = _wrap_binary_strfunc(os.symlink)
        else:
            def symlink(a, b, target_is_directory):
                raise NotImplementedError("symlink() not available on this system")
    else:
        # Under POSIX, os.symlink() takes two args
        @staticmethod
        def symlink(a, b, target_is_directory):
            return os.symlink(str(a), str(b))

    utime = _wrap_strfunc(os.utime)

    # Helper for resolve()
    def readlink(self, path):
        return os.readlink(path)


class GridFSPath(BasePath):
    pass
