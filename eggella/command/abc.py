from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple


class ABCCommandParser(ABC):
    @abstractmethod
    def __call__(self, raw_command: str) -> List[str]:
        pass


class ABCCommandArgumentsCaster(ABC):
    @abstractmethod
    def __call__(self, fn: Callable, tokens: List[str]) -> Tuple[Tuple[Any], Dict[str, Any]]:
        pass


class ABCCommandHandler(ABC):
    @abstractmethod
    def handle(self, fn: Callable[..., Any], text: str):
        pass
