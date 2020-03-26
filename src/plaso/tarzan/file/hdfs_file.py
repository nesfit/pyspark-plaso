# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from dfvfs.path.path_spec import PathSpec
from plaso.tarzan.file.generic_file import FileObject
from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs


class HdfsFileObject(FileObject):
    """HDFS file access."""

    def __init__(self):
        # type: () -> None
        """
        Initializes a HDFS file object.
        """
        self.hdfs = PyArrowHdfs()
        self.path = None
        self.input_stream = None

    def open(self, hdfs_uri, path_spec=None):
        # type: (str, PathSpec) -> None
        """
        Open a HDFS file identified by the HDFS URI and optionally also by its path.
        :param hdfs_uri: the HDFS URI of the file to open
        :param path_spec: the path of the file to open
        """
        self.hdfs.open_filesystem(hdfs_uri)
        self.path = self.hdfs.make_qualified_path(path_spec or hdfs_uri)
        self.input_stream = self.hdfs.open_inputstream(self.path)

    def close(self):
        # type: () -> None
        """
        Close the file.
        """
        self.hdfs.close_stream(self.input_stream)
        self.input_stream = None

    def read(self, size=None):
        # type: (int) -> bytes
        """
        Reads a byte string from the file-like object at the current offset.
        The function will read a byte string of the specified size or all of the remaining data
        if no size was specified.
        :param size: number of bytes to read, where None is all remaining data
        :return: data read
        """
        return self.hdfs.read_inputstream(self.input_stream, size)

    def seek(self, offset, whence=os.SEEK_SET):
        # type: (int, int) -> None
        """
        Set a position in the file for future reading or writing.
        :param offset: the position as an offset
        :param whence: from where the position should be reached (the beginning, the end, etc.)
        """
        self.hdfs.seek_stream(self.input_stream, offset, whence)

    def tell(self):
        # type: () -> int
        """
        Get a current position in the file.
        :return: the current position (an offset)
        """
        return self.hdfs.get_stream_offset(self.input_stream)
