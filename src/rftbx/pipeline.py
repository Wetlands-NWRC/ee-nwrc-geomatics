import abc
from abc import ABCMeta, abstractmethod


class IRandomForestPipeline(metaclass=ABCMeta):
    """ A class that defines the interface for a random forest pipeline. """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'preprocessing') and
                callable(subclass.preprocessing) and
                hasattr(subclass, 'processing') and
                callable(subclass.processing) and
                hasattr(subclass, 'postprocessing') and
                callable(subclass.postprocessing))

    @abstractmethod
    def preprocessing(self):
        raise NotImplementedError

    @abstractmethod
    def processing(self):
        raise NotImplementedError

    @abstractmethod
    def postprocessing(self):
        raise NotImplementedError

