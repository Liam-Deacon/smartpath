smartpath - Smarter URI paths in the style of pathlib
=====================================================

Smartly handle URIs as though they are local files (similar to `pathlib.Path`)

This project was started because I believed there could be an easier way to
handle remote file IO within Python in a uniform and standard's compliant
fashion. There is still a long way to go, but hopefully this shows
proof of concept.

Install
--------

To install, use pip:

```python
pip install smartpath
```

Usage Examples
--------------

To intelligently handle different paths, use `UriPath`:

```python
>>> from smartpath import UriPath
>>> path = UriPath('ftp://localhost/path/to/file')
>>> path
FTPPath('ftp://localhost/path/to/file')
```

All Path classes are designed to behave as close to pathlib.Path
as possible, e.g.

```python
>>> from smartpath import UriPath as SmartPath
>>> path = SmartPath('smb://user:pass@host/path/to/blob')
>>> path
SambaPath('smb://user:pass@host/path/to/blob')
>>> path.exists()
False
```

Supported Formats
-----------------

Currently the following are supported (or semi-supported):

- FTPPath: 'ftp://', 'ftps://' or 'sftp://'
- NFSPath: 'nfs://'
- AzurePath: '(http|https)://*(file|blob).core.windows.net'
- SambaPath: 'smb://' or 'cifs://'
- WebDavPath: 'dav://'

Planned Support
---------------

- S3Path
- GridFSPath
- _dropbox_
- _googledrive_
- _amazondrive_
- _box.com_
- SQL?

To Do
-----

Unit tests!
