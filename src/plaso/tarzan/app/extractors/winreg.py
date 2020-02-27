# -*- coding: utf-8 -*-
"""Tarzan WinReg extractor"""

from plaso.tarzan.app.extractors.extractor import Extractor
from plaso.tarzan.app.extractors.manager import Manager


class WinReg(Extractor):
    """
    Extract events from Windows Registry files.
    """
    __name = "Windows Registry",  # type: str
    __description = "Extract events from Window Registry files"  # type: str

    @classmethod
    def filter(cls, path):
        # type: (str) -> bool
        """
        Check is the file-path is a file-path of a Windows Registry file.
        For the filename extensions see https://en.wikipedia.org/wiki/Windows_Registry#File_locations
        :param path: the file-path to check
        :return: True iff it is a PE file
        """
        # the suffix takes at most the last 20 characters and it is case insensitive, so lowercase that last characters
        return path[-20:].lower().endswith((
            # Windows NT User
            "/ntuser.dat",  # HKEY_CURRENT_USER
            # Windows NT System
            "/sam",  # HKEY_LOCAL_MACHINE\SAM
            "/security",  # HKEY_LOCAL_MACHINE\SECURITY
            "/software",  # HKEY_LOCAL_MACHINE\SOFTWARE
            "/system",  # HKEY_LOCAL_MACHINE\SYSTEM
            "/default",  # HKEY_USERS\.DEFAULT
            "/usrclass.dat"  # file associations and COM information
            # Windows 9x
            "/user.dat",  # HKEY_CURRENT_USER
            "/system.dat",  # HKEY_LOCAL_MACHINE
            "/classes.dat"  # file associations and COM information
        ))

    @classmethod
    def extract(cls, path):
        # type: (str) -> list
        """
        Extract events from a Windows Registry file in the given path.
        :param path: the path of the file to extract
        :return: a lit of events
        """
        from plaso.tarzan.file.hdfs_file import HdfsFileObject
        input_file = HdfsFileObject()
        input_file.open(path)
        from plaso.parsers.winreg import WinRegistryParser
        parser = WinRegistryParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        # parse and read results
        parser.Parse(mediator, input_file)
        return mediator.flush_buffer(exception_on_error=False)


Manager.register_extractor(WinReg)
