from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple


class ABCTokensParser(ABC):
    @abstractmethod
    def __call__(self, raw_command: str) -> List[str]:
        pass


class ABCCommandArgumentsCaster(ABC):
    @abstractmethod
    def __call__(self, fn: Callable, tokens: List[str]) -> Tuple[Tuple[Any], Dict[str, Any]]:
        pass


class ABCCommandHandler(ABC):
    @abstractmethod
    def handle(self, fn: Callable[..., Any], text: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        pass

    def __call__(self, fn: Callable[..., Any], text: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        return self.handle(fn, text)
