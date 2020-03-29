# -*- coding: utf-8 -*-
"""Tarzan Plaso SQLite extractor"""

from __future__ import unicode_literals

import os

from plaso.tarzan.app.extractors.extractor import Extractor
from plaso.tarzan.app.extractors.manager import Manager


class SQLite(Extractor):
    """
    Extract events from SQLite files such as web-browser history files.
    """
    __name = "SQLite"  # type: str
    __description = "Extract events from SQLite files such as web-browser history files"  # type: str

    @classmethod
    def filter(cls, path):
        # type: (str) -> bool
        """
        Check is the file-path is a file-path of an SQLite file.
        :param path: the file-path to check
        :return: True iff it is an SQLite file
        """
        head_tail = os.path.split(path)
        return head_tail[1].endswith((".sqlite", ".db")) or head_tail[1].startswith(("History-")) or (head_tail[1] == "History")

    @classmethod
    def extract(cls, path):
        # type: (str) -> list
        """
        Extract events from an SQLite file in the given path.
        :param path: the path of the file to extract
        :return: a lit of events
        """
        from dfvfs.path.factory import Factory as PathSpecFactory
        from dfvfs.resolver.resolver import Resolver as PathSpecResolver
        from plaso.tarzan.dfvfs2 import definitions
        pathSpec = PathSpecFactory.NewPathSpec(definitions.TYPE_INDICATOR_HDFS, location=path)
        file_entry = PathSpecResolver.OpenFileEntry(pathSpec)
        from plaso.parsers.sqlite import SQLiteParser
        parser = SQLiteParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        mediator.SetFileEntry(file_entry)
        # parse and read results
        parser.Parse(mediator)
        return mediator.flush_buffer(exception_on_error=False)


Manager.register_extractor(SQLite)
