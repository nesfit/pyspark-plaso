# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod


class FileObject(object):
    """Abstract class for a generic file."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def close(self):
        # type: () -> None
        """
        Close the file.
        """
        pass

    @abstractmethod
    def read(self, size):
        # type: (int) -> bytes
        """
        Reads a byte string from the file-like object at the current offset.
        The function will read a byte string of the specified size or all of the remaining data
        if no size was specified.
        :param size: number of bytes to read, where None is all remaining data
        :return: data read
        """
        pass

    @abstractmethod
    def seek(self, offset, whence):
        # type: (int, int) -> None
        """
        Set a position in the file for future reading or writing.
        :param offset: the position as an offset
        :param whence: from where the position should be reached (the beginning, the end, etc.)
        """
        pass
