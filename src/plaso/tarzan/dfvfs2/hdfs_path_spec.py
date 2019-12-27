# -*- coding: utf-8 -*-
"""The HDFS path specification implementation."""

from __future__ import unicode_literals

from dfvfs.path.factory import Factory as PathFactory
from dfvfs.path.location_path_spec import LocationPathSpec
from plaso.tarzan.dfvfs2 import definitions


class HDFSPathSpec(LocationPathSpec):
    """HDFS path specification."""

    _IS_SYSTEM_LEVEL = True
    TYPE_INDICATOR = definitions.TYPE_INDICATOR_HDFS

    def __init__(self, location=None, **kwargs):
        # type: (str, dict) -> None
        """
        Initializes a path specification. Note that the HDFS path specification cannot have a parent.
        :param location: HDFS specific location URI string, e.g., "hdfs://hadoop@namenode:8020/test_data"
        :raises ValueError: when location is not set or parent is set
        """
        if not location:
            raise ValueError('Missing location value (HDFS URI).')
        parent = None
        parent_name = str('parent')
        if parent_name in kwargs:
            parent = kwargs[parent_name]
            del kwargs[parent_name]
        if parent:
            raise ValueError('Parent value set.')
        super(HDFSPathSpec, self).__init__(location=location, parent=parent, **kwargs)


PathFactory.RegisterPathSpec(HDFSPathSpec)
