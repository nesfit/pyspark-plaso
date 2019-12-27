# -*- coding: utf-8 -*-
"""The file system implementation for HDFS."""

from __future__ import unicode_literals

from dfvfs.lib.errors import PathSpecError
from dfvfs.resolver.context import Context
from dfvfs.vfs.file_system import FileSystem
from plaso.tarzan.dfvfs2 import definitions
from plaso.tarzan.dfvfs2.hdfs_file_entry import HDFSFileEntry
from plaso.tarzan.dfvfs2.hdfs_path_spec import HDFSPathSpec
from plaso.tarzan.lib.hdfs import Hdfs
from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs


class HDFSFileSystem(FileSystem):
    """HDFS file system."""

    LOCATION_ROOT = Hdfs.PATH_SEPARATOR
    PATH_SEPARATOR = Hdfs.PATH_SEPARATOR
    TYPE_INDICATOR = definitions.TYPE_INDICATOR_HDFS

    def __init__(self, resolver_context):
        # type: (Context) -> None
        """
        Initializes a file system.
        :param resolver_context: resolver context
        :raises ValueError: if a derived file system class does not define a type indicator
        """
        super(HDFSFileSystem, self).__init__(resolver_context)
        self.hdfs = PyArrowHdfs()

    def _Close(self):
        # type: () -> None
        """
        Closes the file system.
        """
        self.hdfs.close_filesystem()
        return

    def _Open(self, path_spec, mode='rb'):
        # type: (HDFSPathSpec, str) -> None
        """
        Opens the file system defined by path specification.
        :param path_spec: a path specification where its location is an HDFS URI
        :param mode: file access mode. The default is 'rb' which represents read-only binary
        :raises PathSpecError: if the path specification is incorrect
        :raises ValueError: if the path specification is invalid
        """
        if path_spec.HasParent():
            raise PathSpecError('Unsupported path specification with parent.')
        location = getattr(path_spec, 'location', None)
        if location is None:
            raise ValueError('Missing location in the path specification.')
        self.hdfs.open_filesystem(location)

    def FileEntryExistsByPathSpec(self, path_spec):
        # type: (HDFSPathSpec) -> bool
        """
        Determines if a file entry for a path specification exists.
        :param path_spec: a path specification
        :return: True if the file entry exists, false otherwise
        """
        location = getattr(path_spec, 'location', None)
        if location is None:
            return False
        return self.hdfs.exists(location)

    def GetFileEntryByPathSpec(self, path_spec):
        # type: (HDFSPathSpec) -> HDFSFileEntry
        """
        Retrieves a file entry for a path specification.
        :param path_spec: a path specification
        :return: a file entry or None if not available
        """
        if not self.FileEntryExistsByPathSpec(path_spec):
            return None
        return HDFSFileEntry(self._resolver_context, self, path_spec)

    def GetRootFileEntry(self):
        # type: () -> HDFSFileEntry
        """
        Retrieves the root file entry.
        :return: a file entry or None if not available
        """
        location = self.hdfs.make_uri()
        path_spec = HDFSPathSpec(location=location)

        return self.GetFileEntryByPathSpec(path_spec)

    def BasenamePath(self, path):
        # type: (str) -> str
        """Determines the basename of the path.
        :param path: path
        :return: basename of the path
        """
        return self.hdfs.basename(path)

    def DirnamePath(self, path):
        # type: (str) -> str
        """
        Determines the directory name of the path. The file system root is represented by an empty string.
        :param path: path
        :return: directory name of the path or None
        """
        return self.hdfs.dirname(path)

    def JoinPath(self, path_segments, qualified=False):
        # type: (list, bool) -> str
        """
        Joins the path segments into a path.
        :param path_segments: path segments where the first can be a fully qualified HDFS URI
        :param qualified: if the resulting path should be a fully qualified HDFS URI
        :return: joined path segments prefixed with the path separator
        """
        # extract the first segment and use it to make (qualified) base path
        iter_path_segments = iter(path_segments)
        path = iter_path_segments.next()
        if qualified:
            path = self.hdfs.make_qualified_path(path)
        # add other segments
        for path_segment in iter_path_segments:
            path = self.hdfs.append_to_path(path, path_segment)
        return path

    def SplitPath(self, path, qualified=False):
        # type: (str, bool) -> list
        """
        Splits the path into path segments.
        :param path: path
        :param qualified: if the first segment should be an HDFS URI
        :return: path segments without the root path segment, which is an empty string.
        """
        parsed_path = self.hdfs.parse_uri(path)
        # split the path with the path separator and remove empty path segments.
        path_segments = list(filter(None, parsed_path.path.split(self.PATH_SEPARATOR)))
        # if qualified then the first segment is HDFS URI
        if qualified:
            path_segments.insert(0, self.hdfs.make_uri())
        return path_segments
