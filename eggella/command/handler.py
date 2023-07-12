from typing import Any, Callable, Dict, Optional, Tuple

from eggella.command.abc import (
    ABCCommandArgumentsCaster,
    ABCCommandHandler,
    ABCCommandParser,
)
from eggella.command.command import CommandArgumentsCaster, CommandParser


class CommandHandler(ABCCommandHandler):
    def __init__(
        self,
        parser: ABCCommandParser = CommandParser(),
        caster: Optional[ABCCommandArgumentsCaster] = CommandArgumentsCaster(),
    ):
        self.parser = parser
        self.caster = caster

    def handle(self, fn: Callable[..., Any], text: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        arguments = self.parser(text)
        return self.caster(fn, arguments) if self.caster else (tuple(arguments), {})
