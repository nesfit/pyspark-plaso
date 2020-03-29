# -*- coding: utf-8 -*-
"""Tarzan Plaso Dummy extractor"""

from __future__ import unicode_literals

class Extractor(object):
    """
    Serve as a dummy extractor for its sub-classes.
    """
    __name = "Dummy"  # type: str
    __description = "Serve as a dummy extractor for its sub-classes"  # type: str

    @classmethod
    def get_name(cls):
        # type: () -> str
        """
        Get a name of the extractor.
        :return: the name of the extractor
        """
        return cls.__name

    @classmethod
    def get_description(cls):
        # type: () -> str
        """
        Get a description of the extractor.
        :return: the description of the extractor
        """
        return cls.__description

    @classmethod
    def filter(cls, path):
        # type: (str) -> bool
        """
        Check if a file given by its HDFS path can be processed by this extractor.
        :param path: the HDFS path of the file
        :return: true iff the file can be processed
        """
        return True

    @classmethod
    def extract(cls, path):
        # type: (str) -> list
        """
        Extract events from a file given by its HDFS path.
        :param path: the HDFS path of the file
        :return: the list of events
        """
        return []
