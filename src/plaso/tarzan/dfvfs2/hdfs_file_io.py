# -*- coding: utf-8 -*-
"""The HDFS file-like object implementation."""

from __future__ import unicode_literals

import os

from dfvfs.file_io.file_io import FileIO
from dfvfs.lib.errors import PathSpecError
from dfvfs.path.path_spec import PathSpec
from dfvfs.resolver.context import Context
from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs


class HDFSFile(FileIO):
    """File-like object for HDFS."""

    def __init__(self, resolver_context):
        # type: (Context) -> None
        """
        Initializes a file-like object.
        :param resolver_context: resolver context
        """
        super(HDFSFile, self).__init__(resolver_context)
        self._hdfs = PyArrowHdfs()
        self._file_object = None
        self._size = 0

    def _Close(self):
        # type: () -> None
        """
        Closes the file-like object.
        """
        self._file_object.close()
        self._file_object = None

    def _Open(self, path_spec=None, mode='rb'):
        # type: (PathSpec, str) -> None
        """
        Opens the file-like object defined by path specification.
        :param path_spec: path specification
        :param mode: file access mode
        :raises IOError: if the file-like object could not be opened
        :raises PathSpecError: if the path specification is incorrect
        :raises ValueError: if the path specification is invalid
        """
        if not path_spec:
            raise ValueError('Missing path specification.')

        if path_spec.HasParent():
            raise PathSpecError('Unsupported path specification with parent.')

        location = getattr(path_spec, 'location', None)

        if location is None:
            raise PathSpecError('Path specification missing location.')

        if mode != 'rb':
            raise ValueError('Only mode "rb" allowed.')

        try:
            self._hdfs.open_filesystem(location)
            self._file_object = self._hdfs.open_inputstream(location)
            self._size = self._file_object.size()
        except Exception as exception:
            raise IOError('Unable to open file with error: {0!s}.'.format(exception))

    def read(self, size=None):
        # type: (int) -> int
        """
        Reads a byte string from the file-like object at the current offset.
        The function will read a byte string of the specified size or all of the remaining data
        if no size was specified.
        :param size: number of bytes to read, where None is all remaining data.
        :return: data read
        :raises IOError: if the read failed
        """
        if not self._is_open:
            raise IOError('Not opened.')

        if size is None:
            size = self._size - self._file_object.tell()

        return self._file_object.read(size)

    def seek(self, offset, whence=os.SEEK_SET):
        # type: (int, int) -> None
        """
        Seeks to an offset within the file-like object.
        :param offset: offset to seek to
        :param whence: value that indicates whether offset is an absolute or relative position within the file
        :raises IOError: if the seek failed
        """
        if not self._is_open:
            raise IOError('Not opened.')

        # For a yet unknown reason a Python file-like object on Windows allows for
        # invalid whence values to be passed to the seek function. This check
        # makes sure the behavior of the function is the same on all platforms.
        if whence not in [os.SEEK_SET, os.SEEK_CUR, os.SEEK_END]:
            raise IOError('Unsupported whence.')

        self._hdfs.seek_stream(self._file_object, offset, whence)

    def get_offset(self):
        # type: () -> int
        """
        Retrieves the current offset into the file-like object.
        :return: current offset into the file-like object
        :raises: IOError: if the file-like object has not been opened
        """
        if not self._is_open:
            raise IOError('Not opened.')

        return self._file_object.tell()

    def get_size(self):
        # type: () -> int
        """
        Retrieves the size of the file-like object.
        :return: size of the file-like object data
        :raises IOError: if the file-like object has not been opened
        """
        if not self._is_open:
            raise IOError('Not opened.')

        return self._size
