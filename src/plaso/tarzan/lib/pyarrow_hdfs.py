# -*- coding: utf-8 -*-

import os

from pyarrow import HadoopFileSystem, HdfsFile
from pyarrow.hdfs import connect

from plaso.tarzan.lib.hdfs import Hdfs


class PyArrowHdfs(Hdfs):
    """HDFS driver utilizing PyArrow library."""
    fs = None  # type: HadoopFileSystem

    def open_filesystem(self, hdfs_uri, user="hadoop"):
        # type: (str, str) -> HadoopFileSystem
        """
        Open HDFS filesystem of a given URI and as a given HDFS user.
        :param hdfs_uri: HDFS URI to open
        :param user: HDFS user to act as when opening
        :return: the opened filesystem as an object of pyarrow.HadoopFileSystem
        """
        uri = self.parse_uri(hdfs_uri)
        # see https://arrow.apache.org/docs/python/filesystems.html#hadoop-file-system-hdfs
        self.fs = connect(host=uri.hostname or "default", port=uri.port or 0, user=uri.username)
        return self.fs

    def close_filesystem(self, filesystem=None):
        # type: (HadoopFileSystem) -> None
        """
        Close a given HDFS filesystem.
        :param filesystem: the filesystem
        """
        # by default, use the implicit filesystem
        if filesystem is None:
            self.fs = None
        # see https://arrow.apache.org/docs/python/filesystems.html#hadoop-file-system-hdfs
        # pyarrow does not support closing the filesystem

    def get_filesystem(self, force_filesystem=None):
        # type: (HadoopFileSystem) -> HadoopFileSystem
        """
        Get a given or a default HDFS filesystem.
        :param force_filesystem: the given filesystem
        :return: the filesystem
        """
        return force_filesystem or self.fs

    def exists(self, path_string, filesystem=None):
        # type: (str, HadoopFileSystem) -> bool
        """
        Check if a given HDFS path exists in the given HDFS filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: True if the path exists in the filesystem, False otherwise
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.make_simple_path(path_string, filesystem)
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.exists.html#pyarrow.HadoopFileSystem.exists
        return filesystem.exists(simple_path)

    def info(self, path_string, filesystem=None):
        # type: (str, HadoopFileSystem) -> dict
        """
        Get metadata of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: the metadata dictionary
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path_string).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.info.html#pyarrow.HadoopFileSystem.info
        return filesystem.info(simple_path)

    def remove(self, path_string, recursive=True, filesystem=None):
        # type: (str, bool, HadoopFileSystem) -> None
        """
        Remove (optionally recursively) a HDFS file/directory given by its path in a given or a default filesystem.
        :param path_string: the path
        :param recursive: True to remove recursively
        :param filesystem: the filesystem
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path_string).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.rm.html#pyarrow.HadoopFileSystem.rm
        filesystem.rm(simple_path, recursive)

    def mkdir(self, path_string, filesystem=None):
        # type: (str, HadoopFileSystem) -> None
        """
        Make a new directory (if does not exist) of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path_string).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.mkdir.html#pyarrow.HadoopFileSystem.mkdir
        filesystem.mkdir(simple_path)

    def list_files(self, path_string, recursion_level=0, include_dir_names=False, filesystem=None):
        # type: (str, int, bool, HadoopFileSystem) -> list
        """
        Get a list of files (optionally recursively to the specified level) in a given HDFS path of a given filesystem.
        :param path_string: the path
        :param recursion_level: the level for the recursion (0 is just a current directory without any recursion)
        :param include_dir_names: True to include also names of directories (suffixed by /)
        :param filesystem: the filesystem
        :return: the list of files in the path
        """
        # exit on negative recursion level (cannot read the current level)
        if recursion_level < 0:
            return []
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path_string).path
        # get items
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.ls.html#pyarrow.HadoopFileSystem.ls
        status_items = filesystem.ls(path=simple_path, detail=True)
        result = []
        for file_status in status_items:
            if file_status["kind"] == "file":
                result.append(self.make_qualified_path(file_status["name"], filesystem))
            elif file_status["kind"] == "directory":
                if include_dir_names:
                    result.append(self.make_qualified_path(file_status["name"], filesystem) + "/")
                result.extend(self.list_files(file_status["name"], recursion_level - 1, include_dir_names, filesystem))
        return result

    def open_inputstream(self, path, filesystem=None):
        # type: (str, HadoopFileSystem) -> HdfsFile
        """
        Open and get an input-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened input-stream
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.open.html#pyarrow.HadoopFileSystem.open
        return filesystem.open(simple_path, mode="rb")

    def open_outputstream(self, path, filesystem=None):
        # type: (str, HadoopFileSystem) -> HdfsFile
        """
        Open and get an output-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened output-stream
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.open.html#pyarrow.HadoopFileSystem.open
        return filesystem.open(simple_path, mode="wb")

    def close_stream(self, input_stream):
        # type: (HdfsFile) -> None
        """
        Close a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.close
        input_stream.close()

    def get_stream_offset(self, input_stream):
        # type: (HdfsFile) -> int
        """
        Get the current position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        :return: the position/offset
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.tell
        return input_stream.tell()

    def get_path_size(self, path, filesystem=None):
        # type: (str, HadoopFileSystem) -> int
        """
        Get the size of a given HDFS path (a file) in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the size
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        simple_path = self.parse_uri(path).path
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HadoopFileSystem.disk_usage.html#pyarrow.HadoopFileSystem.disk_usage
        return filesystem.disk_usage(simple_path)

    def read_inputstream(self, input_stream, size=None):
        # type: (HdfsFile, int) -> bytes
        """
        Read data form a given opened input stream for a HDFS file.
        :param input_stream: the input-stream
        :param size: the size of data to read
        :return: the data
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.read
        return input_stream.read(size)

    def write_outputstream(self, output_stream, data):
        # type: (HdfsFile, bytes) -> int
        """
        Write data buffer to a given opened output stream for a HDFS file.
        :param output_stream: the output-stream
        :param data: the data buffer to write
        :return: the number of bytes written
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.write
        return output_stream.write(data)

    def pass_to_outputstream(self, output_stream, input_stream):
        # type: (HdfsFile, object) -> None
        """
        Pass data from the input stream to the output stream to a HDFS file.
        :param output_stream: the output-stream of the HDFS file
        :param input_stream: the input-stream
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.upload
        output_stream.upload(input_stream)

    def seek_stream(self, stream, offset, whence=os.SEEK_SET):
        # type: (HdfsFile, int, int) -> None
        """
        Set a given position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param stream: the opened stream
        :param offset: the position/offset
        :param whence: the direction
        """
        # see https://arrow.apache.org/docs/python/generated/pyarrow.HdfsFile.html#pyarrow.HdfsFile.seek
        if whence == os.SEEK_SET:
            stream.seek(offset, whence=0)
        elif whence == os.SEEK_CUR:
            stream.seek(offset, whence=1)
        elif whence == os.SEEK_END:
            stream.seek(offset, whence=2)
