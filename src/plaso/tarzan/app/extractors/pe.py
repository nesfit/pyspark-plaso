# -*- coding: utf-8 -*-
"""Tarzan Plaso PE extractor"""

from __future__ import unicode_literals

from plaso.tarzan.app.extractors.extractor import Extractor
from plaso.tarzan.app.extractors.manager import Manager


class PE(Extractor):
    """
    Extract events from Portable Executable (PE) files.
    """
    __name = "Portable Executable",  # type: str
    __description = "Extract events from Portable Executable (PE) files" \
                    " such as executables, object code, DLLs, FON Font files, and others"  # type: str

    @classmethod
    def filter(cls, path):
        # type: (str) -> bool
        """
        Check is the file-path is a file-path of a PE file.
        For the filename extensions see https://en.wikipedia.org/wiki/Portable_Executable
        :param path: the file-path to check
        :return: True iff it is a PE file
        """
        return path.endswith(
            (".acm", ".ax", ".cpl", ".dll", ".drv", ".efi", ".exe", ".mui", ".ocx", ".scr", ".sys", ".tsp"))

    @classmethod
    def extract(cls, path):
        # type: (str) -> list
        """
        Extract events from a PE file in the given path.
        :param path: the path of the file to extract
        :return: a lit of events
        """
        from plaso.tarzan.file.hdfs_file import HdfsFileObject
        input_file = HdfsFileObject()
        input_file.open(path)
        from plaso.parsers.pe import PEParser
        parser = PEParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        # parse and read results
        parser.Parse(mediator, input_file)
        return mediator.flush_buffer(exception_on_error=False)


Manager.register_extractor(PE)
