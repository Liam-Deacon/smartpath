import libnfs

from .base import BasePath, BaseClient


class NFSPath(BasePath):
    pass


class NFSClient(libnfs.NFS, BaseClient):
    def __init__(self, *args, **kwargs):
        super(libnfs.NFSClient, self).__init__(*args, **kwargs)
