# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from dfvfs.path.path_spec import PathSpec
from plaso.tarzan.file.generic_file import FileObject


class LocalFileObject(FileObject):
    """Local file access."""

    def __init__(self):
        # type: () -> None
        """
        Initializes a local file object.
        """
        self.path = None
        self.file_object = None

    def open(self, path_spec=None, mode='rb'):
        # type: (PathSpec, str) -> None
        """
        Open a local file identified by its path and in a particular mode.
        :param path_spec: the path of the file to open
        :param mode: the mode of the file opening (and its future usage, i.e., reading, writing, etc.)
        """
        self.path = path_spec.comparable
        self.file_object = open(self.path, mode)

    def close(self):
        # type: () -> None
        """
        Close the file.
        """
        self.file_object.close()

    def read(self, size=None):
        # type: (int) -> bytes
        """
        Reads a byte string from the file-like object at the current offset.
        The function will read a byte string of the specified size or all of the remaining data
        if no size was specified.
        :param size: number of bytes to read, where None is all remaining data
        :return: data read
        :raises IOError: if the read failed
        :raises OSError: if the read failed
        """
        if size is None:
            return self.file_object.read()
        else:
            return self.file_object.read(size)

    def seek(self, offset, whence=os.SEEK_SET):
        # type: (int, int) -> None
        """
        Set a position in the file for future reading or writing.
        :param offset: the position as an offset
        :param whence: from where the position should be reached (the beginning, the end, etc.)
        """
        self.file_object.seek(offset, whence)

    def tell(self):
        # type: () -> int
        """
        Get a current position in the file.
        :return: the current position (an offset)
        """
        return self.file_object.tell()
