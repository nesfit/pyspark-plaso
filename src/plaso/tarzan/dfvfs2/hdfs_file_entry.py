# -*- coding: utf-8 -*-
"""The HDFS file entry implementation."""

from __future__ import unicode_literals

import stat

from dfdatetime import posix_time as dfdatetime_posix_time
from dfdatetime.interface import DateTimeValues

from dfvfs.lib import definitions as plaso_definitions
from dfvfs.lib.errors import BackEndError
from dfvfs.resolver.context import Context
from dfvfs.vfs.file_entry import Directory, FileEntry
from dfvfs.vfs.file_system import FileSystem
from dfvfs.vfs.vfs_stat import VFSStat
from plaso.tarzan.dfvfs2 import definitions
# DO NOT: import plaso.tarzan.dfvfs2.hdfs_path_spec.HDFSFileSystem
# as it will result into cyclic imports when HDFSFileSystem invoked import of HDFSFileEntry and is empty here
# see https://groups.google.com/forum/#!topic/comp.lang.python/HYChxtsrhnw
from plaso.tarzan.dfvfs2.hdfs_path_spec import HDFSPathSpec


class HDFSDirectory(Directory):
    """HDFS directory."""

    def _EntriesGenerator(self):
        # type: () -> Generator[HDFSPathSpec,None,None]
        """
        Retrieves directory entries. Since a directory can contain a vast number of entries using a generator is more memory efficient.
        :return: generator of path specifications
        :raises BackEndError: if the directory could not be listed
        """
        location = getattr(self.path_spec, 'location', None)
        if location and getattr(self._file_system, 'hdfs', None):
            try:
                for directory_entry in self._file_system.hdfs.list_files(location, recursion_level=0):
                    directory_entry_location = self._file_system.JoinPath([location, directory_entry])
                    yield HDFSPathSpec(location=directory_entry_location)

            except Exception as exception:
                raise BackEndError(
                    'Unable to list directory: {0:s} with error: {1!s}'.format(location, exception))


class HDFSFileEntry(FileEntry):
    """HDFS file entry."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_HDFS

    def __init__(self, resolver_context, file_system, path_spec, is_root=False):
        # type: (Context, FileSystem, HDFSPathSpec, bool) -> None
        """
        Initializes a file entry.
        :param resolver_context: resolver context
        :param file_system: file system
        :param path_spec: path specification
        :param is_root: True if the file entry is the root file entry of the corresponding file system
        :raises BackEndError: If there is a HDFS backend error
        """
        location = getattr(path_spec, 'location', None)

        path_info = None
        if location and getattr(file_system, 'hdfs', None):
            try:
                # cannot import HDFSFileSystem due to cyclic dependency, so using its superclass FileSystem
                path_info = file_system.hdfs.info(location)
            except Exception as exception:
                raise BackEndError('Unable to retrieve path_info dictionary with error: {0!s}'.format(exception))

        super(HDFSFileEntry, self).__init__(resolver_context, file_system, path_spec, is_root=is_root, is_virtual=False)
        self._name = None
        self._path_info = path_info

        if path_info:
            if path_info["kind"] == "symlink":
                # symlinks in HDFS are not supported currently, see https://issues.apache.org/jira/browse/HADOOP-10019
                self.entry_type = plaso_definitions.FILE_ENTRY_TYPE_LINK
            elif path_info["kind"] == "file":
                self.entry_type = plaso_definitions.FILE_ENTRY_TYPE_FILE
            elif path_info["kind"] == "directory":
                self.entry_type = plaso_definitions.FILE_ENTRY_TYPE_DIRECTORY

    def _GetDirectory(self):
        # type: () -> HDFSDirectory
        """
        Retrieves a directory.
        :return: a directory object or None if not available
        """
        if self.entry_type != plaso_definitions.FILE_ENTRY_TYPE_DIRECTORY:
            return None
        return HDFSDirectory(self._file_system, self.path_spec)

    def _GetLink(self):
        # type: () -> unicode
        """
        Retrieves the link.
        :return: the link
        """
        if self._link is None:
            self._link = ''

            if not self.IsLink():
                return self._link

            # symlinks in HDFS are not supported currently, see https://issues.apache.org/jira/browse/HADOOP-10019

        return self._link

    def _GetStat(self):
        # type: () -> VFSStat
        """
        Retrieves information about the file entry.
        :return: a stat object or None if not available
        """
        stat_object = super(HDFSFileEntry, self)._GetStat()

        if self._path_info:
            # File data stat information.
            stat_object.size = self._path_info["size"]

            # Ownership and permissions stat information.
            stat_object.mode = stat.S_IMODE(int(self._path_info["permissions"]))
            stat_object.uid = self._path_info["owner"]  # it is string; should be number?
            stat_object.gid = self._path_info["group"]  # it is string; should be number?

        return stat_object

    def _GetSubFileEntries(self):
        # type: () -> Generator[HDFSFileEntry,None,None]
        """
        Retrieves sub file entries.
        :return: a sub file entry
        """
        if self._directory is None:
            self._directory = self._GetDirectory()

        if self._directory:
            for path_spec in self._directory.entries:
                yield HDFSFileEntry(self._resolver_context, self._file_system, path_spec)

    @property
    def access_time(self):
        # type: () -> DateTimeValues
        """
        Access time or None if not available.
        """
        if self._path_info is None:
            return None

        timestamp = int(self._path_info["last_accessed"])
        return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

    @property
    def change_time(self):
        # type: () -> DateTimeValues
        """
        Change time or None if not available.
        """
        # change-time is not implemented in HDFS, will be same as the modification-time
        return self.modification_time

    @property
    def link(self):
        # type: () -> unicode
        """
        Full path of the linked file entry.
        """
        return self._GetLink()

    @property
    def name(self):
        # type: () -> str
        """
        Name of the file entry, without the full path.
        """
        if self._name is None:
            location = getattr(self.path_spec, 'location', None)
            if location is not None:
                self._name = self._file_system.BasenamePath(location)
        return self._name

    @property
    def modification_time(self):
        # type: () -> DateTimeValues
        """
        Modification time or None if not available.
        """
        if self._path_info is None:
            return None

        timestamp = int(self._path_info["last_modified"])
        return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

    def GetLinkedFileEntry(self):
        # type: () -> HDFSFileEntry
        """
        Retrieves the linked file entry, for example for a symbolic link.
        :return: linked file entry or None if not available
        """
        link = self._GetLink()
        if not link:
            return None

        path_spec = HDFSPathSpec(location=link)
        return HDFSFileEntry(self._resolver_context, self._file_system, path_spec)

    def GetParentFileEntry(self):
        # type: () -> HDFSFileEntry
        """
        Retrieves the parent file entry.
        :return: parent file entry or None if not available
        """
        location = getattr(self.path_spec, 'location', None)
        if location is None:
            return None

        parent_location = self._file_system.DirnamePath(location)
        if parent_location is None:
            return None

        if parent_location == '':
            parent_location = self._file_system.PATH_SEPARATOR

        path_spec = HDFSPathSpec(location=parent_location)
        return HDFSFileEntry(self._resolver_context, self._file_system, path_spec)
