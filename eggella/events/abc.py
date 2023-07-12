from abc import ABC, abstractmethod


class ABCEvent(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass
