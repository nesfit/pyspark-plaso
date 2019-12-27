# -*- coding: utf-8 -*-
"""The HDFS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.resolver.context import Context
from dfvfs.resolver_helpers.manager import ResolverHelperManager
from dfvfs.resolver_helpers.resolver_helper import ResolverHelper
from plaso.tarzan.dfvfs2 import definitions
from plaso.tarzan.dfvfs2.hdfs_file_io import HDFSFile
from plaso.tarzan.dfvfs2.hdfs_file_system import HDFSFileSystem


class HDFSResolverHelper(ResolverHelper):
    """HDFS resolver helper."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_HDFS

    def NewFileObject(self, resolver_context):
        # type: (Context) -> HDFSFile
        """
        Creates a new file-like object.
        :param resolver_context: resolver context
        :return: file-like object
        """
        return HDFSFile(resolver_context)

    def NewFileSystem(self, resolver_context):
        # type: (Context) -> HDFSFileSystem
        """
        Creates a new file system object.
        :param resolver_context: resolver context
        :return:: file system
        """
        return HDFSFileSystem(resolver_context)


ResolverHelperManager.RegisterHelper(HDFSResolverHelper())
