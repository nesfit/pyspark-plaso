# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pprint import pprint

from dfvfs.path.path_spec import PathSpec
from plaso.tarzan.mediator.mediator import Mediator


class PrintMediator(Mediator):
    """Tarzan mediator printing events to stdout."""

    def __init__(self):
        # type: () -> None
        """
        Initialize the mediator.
        """
        super(PrintMediator, self).__init__()

    def ProduceEventWithEventData(self, event, event_data):
        # type: (dict, dict) -> None
        """
        Produce a particular event with its data.
        :param event: the event
        :param event_data: the event's data
        """
        print("event produced")
        print("Event:")
        print(pprint(vars(event)))
        print("Event data:")
        print(pprint(vars(event_data)))

    def ProduceExtractionError(self, message, path_spec=None):
        # type: (str, PathSpec) -> None
        """
        Produce an extraction error with a particular message and a path.
        :param message: the error message
        :param path_spec: the erroneous path
        """
        print("ERROR " + message)
        print(pprint(vars(path_spec)))

    def ProduceExtractionWarning(self, message, path_spec=None):
        # type: (str, PathSpec) -> None
        """
        Produce an extraction warning with a particular message and a path.
        :param message: the warning message
        :param path_spec: the path that caused the warning
        """
        print("WARNING " + message)
        print(pprint(vars(path_spec)))
