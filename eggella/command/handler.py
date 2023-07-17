from typing import Any, Callable, Dict, Optional, Tuple

from eggella.command.abc import (
    ABCCommandArgumentsCaster,
    ABCCommandHandler,
    ABCCommandParser,
)
from eggella.command.arg_caster import CommandArgumentsCaster
from eggella.command.parser import CommandParser, CommandParserRaw


class CommandHandler(ABCCommandHandler):
    """default command argument. Split args by `shlex.split` function and cast type from function annotations"""

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


class RawCommandHandler(CommandHandler):
    """disable arguments parse and return raw string"""

    def __init__(self, parser=CommandParserRaw(), caster=None):
        super().__init__(parser, caster)
