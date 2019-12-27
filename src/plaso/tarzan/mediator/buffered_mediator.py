# -*- coding: utf-8 -*-

from Queue import Queue
from collections import namedtuple

from dfvfs.path.path_spec import PathSpec
from plaso.tarzan.mediator.mediator import Mediator


class BufferedMediator(Mediator):
    """Tarzan mediator putting events into a buffer."""

    def __init__(self, buffer_queue=None):
        # type: (Queue) -> None
        """
        Initialize the mediator including its queue if not given.
        """
        super(BufferedMediator, self).__init__()
        self.buffer_queue = buffer_queue or Queue()
        self.Event = namedtuple("Event", ["event", "event_data"])
        self.Error = namedtuple("Error", ["message", "path_spec"])

    def ProduceEventWithEventData(self, event, event_data):
        # type: (dict, dict) -> None
        """
        Produce a particular event with its data.
        :param event: the event
        :param event_data: the event's data
        """
        self.buffer_queue.put(item=self.Event(event, event_data))

    def ProduceExtractionError(self, message, path_spec=None):
        # type: (str, PathSpec) -> None
        """
        Produce an extraction error with a particular message and a path.
        :param message: the error message
        :param path_spec: the erroneous path
        """
        self.buffer_queue.put(item=self.Error(message, path_spec))

    def get_buffer_queue(self):
        # type: () -> Queue
        """
        Get the queue of buffered events.
        :return: the queue
        """
        return self.buffer_queue

    def flush_buffer(self, exception_on_error=False):
        # type: (bool) -> list
        """
        Flush the buffer into a list of events and return the list.
        :param exception_on_error: True to raise an exception of an error event.
        :return: the list
        """
        events = []
        while not self.buffer_queue.empty():
            item = self.buffer_queue.get()
            if isinstance(item, self.Event):
                events.append((item.event, item.event_data))
            elif isinstance(item, self.Error) and exception_on_error:
                raise Exception("Extraction error: '%s' at '%s'" % (item.message, item.path_spec), item)
            self.buffer_queue.task_done()
        return events


if __name__ == "__main__":
    buffered_mediator = BufferedMediator()


    def generate(bm):
        for i in range(10):
            if i % 5 == 0:
                bm.ProduceExtractionError("error for %d" % i, "path spec for %d" % i)
            else:
                bm.ProduceEventWithEventData(i, "event data for %d" % i)


    # ignoring errors
    generate(buffered_mediator)
    result = buffered_mediator.flush_buffer()
    print(result)
    # stopping on an error
    generate(buffered_mediator)
    result = buffered_mediator.flush_buffer(exception_on_error=True)
    print(result)
