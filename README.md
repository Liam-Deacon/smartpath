smartpath - Smarter URI paths in the style of pathlib
=====================================================

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
>>> UriPath('ftp://localhost/path/to/file')
FTPPath('ftp://localhost/path/to/file')
```
