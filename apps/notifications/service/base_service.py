from abc import ABC, abstractmethod


class BaseServiceMixin(ABC):
    @staticmethod
    @abstractmethod
    def send(*args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def can_send(*args, **kwargs):
        raise NotImplementedError()
