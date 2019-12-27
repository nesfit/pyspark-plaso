# -*- coding: utf-8 -*-
import os
from abc import ABCMeta, abstractmethod

from future.moves.urllib.parse import urlparse, ParseResult


class Hdfs:
    """An abstract class for drivers to access HDFS."""
    __metaclass__ = ABCMeta

    PATH_SEPARATOR = '/'  # type: str
    SCHEME = 'hdfs'  # type: str

    @staticmethod
    def parse_uri(hdfs_uri):
        # type: (str) -> ParseResult
        """
        Parse HDFS URI into individual components.
        :param hdfs_uri: HDFS URI of the file to parse
        :return: an object that provide individual component of the URI
        """
        # Python 2 and 3 compatibility, see https://www.python-future.org/standard_library_imports.html#aliased-imports
        # see https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
        uri = urlparse(hdfs_uri, scheme=Hdfs.SCHEME)
        if uri.scheme != Hdfs.SCHEME:
            raise Exception("Cannot open HDFS URI with scheme %s!" % uri.scheme)
        return uri

    def make_uri(self, filesystem=None):
        # type: (object) -> str
        """
        Get HDFS URI of a given or a default filesystem.
        :param filesystem: the filesystem
        :return: the HDFS URI
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        if filesystem is None:
            raise Exception("The filesystem must be set either as the 'fs' attribute or the 'filesystem' parameter!")
        # see self.parse_uri(...)
        return "hdfs://%s@%s:%d%s" % (filesystem.user, filesystem.host, filesystem.port, Hdfs.PATH_SEPARATOR) if (
                filesystem.user is not None) else "hdfs://%s:%d%s" % (
            filesystem.host, filesystem.port, Hdfs.PATH_SEPARATOR)

    @abstractmethod
    def open_filesystem(self, hdfs_uri, user):
        # type: (str, str) -> object
        """
        Open HDFS filesystem of a given URI and as a given HDFS user.
        :param hdfs_uri: HDFS URI to open
        :param user: HDFS user to act as when opening
        :return: the opened filesystem
        """
        pass

    @abstractmethod
    def close_filesystem(self, filesystem):
        # type: (str) -> None
        """
        Close a given HDFS filesystem.
        :param filesystem: the filesystem
        """
        pass

    @abstractmethod
    def get_filesystem(self, force_filesystem):
        # type: (object) -> object
        """
        Get a given or a default HDFS filesystem.
        :param force_filesystem: the given filesystem
        :return: the filesystem
        """
        pass

    @abstractmethod
    def exists(self, path_string, filesystem):
        # type: (str, object) -> bool
        """
        Check if a given HDFS path exists in the given HDFS filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: True if the path exists in the filesystem, False otherwise
        """
        pass

    def make_path(self, path_string, qualified=True, filesystem=None):
        # type: (str, bool, object) -> str
        """
        Get a (qualified) HDFS URI from a given path and a given or a default filesystem.
        :param path_string: the path
        :param qualified: True to get the qualified path
        :param filesystem: the filesystem
        :return: the resulting path
        """
        parsed_path = self.parse_uri(path_string)
        # unqualified path is without HDFS URI hostname (it is not HDFS URI, just path)
        if not qualified:
            return parsed_path.path or path_string
        # by default, use the implicit filesystem
        if parsed_path.hostname is None:
            filesystem = self.get_filesystem(filesystem)
        if filesystem is not None:
            normalized_path = parsed_path.path
            if normalized_path[0] == Hdfs.PATH_SEPARATOR:
                normalized_path = normalized_path[1:]
            return self.make_uri(filesystem) + normalized_path
        else:
            return path_string

    def make_simple_path(self, path_string, filesystem=None):
        # type: (str, object) -> str
        """
        Get an unqualified HDFS URI from a given path and a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: the resulting path
        """
        return self.make_path(path_string, False, filesystem)

    def make_qualified_path(self, path_string, filesystem=None):
        # type: (str, object) -> str
        """
        Get a qualified HDFS URI from a given path and a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: the resulting path
        """
        return self.make_path(path_string, True, filesystem)

    def append_to_path(self, original_path, new_child_string):
        # type: (str, str) -> str
        """
        Append a path/directory/file into another HDFS path.
        :param original_path: the another path
        :param new_child_string: the path to append
        :return: the resulting path
        """
        return original_path + Hdfs.PATH_SEPARATOR + self.make_simple_path(new_child_string)

    def __split_path(self, path_string):
        # type: (str) -> (str,str,str)
        """
        Split a given HDFS path into components.
        :param path_string: the path
        :return: the components as a triplet (dirname, _, basename)
        """
        simple_path = self.make_simple_path(path_string)
        # just / for a root directory is also basename
        if simple_path == self.PATH_SEPARATOR:
            return simple_path
        # remove ending / is necessary
        if simple_path.endswith(self.PATH_SEPARATOR):
            simple_path = simple_path[:-1]
        # return the components
        return simple_path.rpartition(self.PATH_SEPARATOR)

    def basename(self, path_string):
        # type: (str) -> str
        """
        Get a basename from a given HDFS path.
        :param path_string: the path
        :return: the basename
        """
        # use the last component after the last /
        _, _, basename = self.__split_path(path_string)
        return basename

    def dirname(self, path_string):
        # type: (str) -> str
        """
        Get a dirname from a given HDFS path.
        :param path_string: the path
        :return: the dirname
        """
        # use the first component before the last /
        dirname, _, _ = self.__split_path(path_string)
        return dirname

    @abstractmethod
    def info(self, path_string, filesystem=None):
        # type: (str, object) -> dict
        """
        Get metadata of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: the metadata dictionary
        """
        pass

    @abstractmethod
    def remove(self, path_string, recursive=True, filesystem=None):
        # type: (str, bool, object) -> None
        """
        Remove (optionally recursively) a HDFS file/directory given by its path in a given or a default filesystem.
        :param path_string: the path
        :param recursive: True to remove recursively
        :param filesystem: the filesystem
        """
        pass

    @abstractmethod
    def mkdir(self, path_string, filesystem=None):
        # type: (str, object) -> None
        """
        Make a new directory (if does not exist) of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        """
        pass

    @abstractmethod
    def list_files(self, path_string, recursion_level=0, include_dir_names=False, filesystem=None):
        # type: (str, int, bool, object) -> list
        """
        Get a list of files (optionally recursively to the specified level) in a given HDFS path of a given filesystem.
        :param path_string: the path
        :param recursion_level: the level for the recursion (0 is just a current directory without any recursion)
        :param include_dir_names: True to include also names of directories (suffixed by /)
        :param filesystem: the filesystem
        :return: the list of files in the path
        """
        pass

    @abstractmethod
    def open_inputstream(self, path, filesystem):
        # type: (str, object) -> object
        """
        Open and get an input-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened input-stream
        """
        pass

    @abstractmethod
    def open_outputstream(self, path, filesystem=None):
        # type: (str, object) -> object
        """
        Open and get an output-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened output-stream
        """
        pass

    @abstractmethod
    def close_stream(self, input_stream):
        # type: (object) -> None
        """
        Close a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        """
        pass

    @abstractmethod
    def get_stream_offset(self, input_stream):
        # type: (object) -> int
        """
        Get the current position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        :return: the position/offset
        """
        pass

    @abstractmethod
    def get_path_size(self, path, filesystem):
        # type: (str, object) -> int
        """
        Get the size of a given HDFS path (a file) in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the size
        """
        pass

    @abstractmethod
    def read_inputstream(self, input_stream, size):
        # type: (object, int) -> bytes
        """
        Read data form a given opened input stream for a HDFS file.
        :param input_stream: the input-stream
        :param size: the size of data to read
        :return: the data
        """
        pass

    @abstractmethod
    def write_outputstream(self, output_stream, data):
        # type: (object, bytes) -> int
        """
        Write data buffer to a given opened output stream for a HDFS file.
        :param output_stream: the output-stream
        :param data: the data buffer to write
        :return: the number of bytes written
        """
        pass

    @abstractmethod
    def seek_stream(self, stream, offset, whence=os.SEEK_SET):
        # type: (object, int, int) -> None
        """
        Set a given position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param stream: the opened stream
        :param offset: the position/offset
        :param whence: the direction
        """
        pass
