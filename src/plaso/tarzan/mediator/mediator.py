# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod

from dfvfs.path.path_spec import PathSpec
from dfvfs.vfs.file_entry import FileEntry
from plaso.parsers.interface import BaseParser


class Mediator(object):
    """An abstract base-class for Tarzan mediators."""
    __metaclass__ = ABCMeta

    def __init__(self):
        # type: () -> None
        """
        Initialize the mediator.
        """
        self._extra_event_attributes = {}
        self.file_entry = None
        self.parser_chain_components = []
        self.collection_filters_helper = None  # accessed by winreg, probably not required
        self.codepage = 'cp1252'  # accessed by winreg plugins, TODO configure properly?

    @abstractmethod
    def ProduceEventWithEventData(self, event, event_data):
        # type: (dict, dict) -> None
        """
        Produce a particular event with its data.
        :param event: the event
        :param event_data: the event's data
        """
        pass

    @abstractmethod
    def ProduceExtractionError(self, message, path_spec):
        # type: (str, PathSpec) -> None
        """
        Produce an extraction error with a particular message and a path.
        :param message: the error message
        :param path_spec: the erroneous path
        """
        pass

    def SetFileEntry(self, file_entry):
        # type: (FileEntry) -> None
        """
        Sets the active file entry.
        :param file_entry: file entry
        """
        self.file_entry = file_entry

    def GetFileEntry(self):
        # type: () -> FileEntry
        """
        Retrieves the active file entry.
        :return: file entry
        """
        return self.file_entry

    def GetFilename(self):
        # type: () -> unicode
        """
        Retrieves the name of the active file entry.
        :return: name of the active file entry or None
        """
        if not self.file_entry:
            return None
        data_stream = getattr(self.file_entry.path_spec, 'data_stream', None)
        if data_stream:
            return '{0:s}:{1:s}'.format(self.file_entry.name, data_stream)
        return self.file_entry.name

    def AppendToParserChain(self, plugin_or_parser):
        # type: (BaseParser) -> None
        """
        Adds a parser or parser plugin to the parser chain.
        :param plugin_or_parser: parser or parser plugin
        """
        self.parser_chain_components.append(plugin_or_parser.NAME)

    def PopFromParserChain(self):
        # type: () -> None
        """
        Removes the last added parser or parser plugin from the parser chain.
        """
        self.parser_chain_components.pop()

    def AddEventAttribute(self, attribute_name, attribute_value):
        # type: (str, str) -> None
        """
        Adds an attribute that will be set on all events produced.
        Setting attributes using this method will cause events produced via this
        mediator to have an attribute with the provided name set with the
        provided value.
        :param attribute_name: name of the attribute to add
        :param attribute_value: value of the attribute to add
        :raises KeyError: if the event attribute is already set
        """
        if attribute_name in self._extra_event_attributes:
            raise KeyError('Event attribute {0:s} already set'.format(
                attribute_name))
        self._extra_event_attributes[attribute_name] = attribute_value

    def RemoveEventAttribute(self, attribute_name):
        # type: (str) -> None
        """
        Removes an attribute from being set on all events produced.
        :param attribute_name: name of the attribute to remove
        :raises KeyError: if the event attribute is not set
        """
        if attribute_name not in self._extra_event_attributes:
            raise KeyError('Event attribute: {0:s} not set'.format(attribute_name))
        del self._extra_event_attributes[attribute_name]

    @property
    def abort(self):
        # type: () -> bool
        """
        Check if the parsing should be aborted.
        :return: True if parsing should be aborted
        """
        return False

    @property
    def temporary_directory(self):
        # type: () -> unicode
        """
        A path of the directory for temporary files.
        :return: path of the directory for temporary files.
        """
        return "/tmp"
