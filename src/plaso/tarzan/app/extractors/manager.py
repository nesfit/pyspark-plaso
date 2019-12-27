# -*- coding: utf-8 -*-
"""The extractors manager"""

from extractor import Extractor


class Manager(object):
    """
    Manager of extractors.
    """
    __extractors_classes = {}

    @classmethod
    def get_extractors(cls):
        # type: () -> list
        """
        Get a list of registered extractor classes.
        :return: the list of extractor classes
        """
        return cls.__extractors_classes.values()

    @classmethod
    def deregister_extractor(cls, extractor_class):
        # type: (type) -> None
        """
        De-registers an extractor class.
        :param extractor_class: extractor class (subclass of Extractor)
        :raise KeyError: if extractor class is not set for the corresponding name
        """
        extractor_name = extractor_class.__name__
        if extractor_name not in cls.__extractors_classes:
            raise KeyError('Extractor class not set for name: {0:s}.'.format(extractor_name))
        del cls.__extractors_classes[extractor_name]

    @classmethod
    def register_extractor(cls, extractor_class):
        # type: (type) -> None
        """
        Registers an extractor class.
        :param extractor_class: extractor class (subclass of Extractor)
        :raise KeyError: if extractor class is already set for the corresponding name
        """
        extractor_name = extractor_class.__name__
        if not issubclass(extractor_class, Extractor):
            raise TypeError(
                'Extractor class {0:s} must be subclass of class {0:s}.'.format(extractor_name, Extractor.__name__))
        if extractor_name in cls.__extractors_classes:
            raise KeyError('Extractor class already set for name: {0:s}.'.format(extractor_name))
        cls.__extractors_classes[extractor_name] = extractor_class
