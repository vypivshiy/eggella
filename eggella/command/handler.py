from typing import Any, Callable, Dict, List, Optional, Tuple

from eggella.command.abc import ABCCommandHandler
from eggella.command.arg_caster import CommandArgumentsCaster
from eggella.command.parser import TokensParser, TokensParserRaw

ARGS_AND_KWARGS = Tuple[Tuple[Any], Dict[str, Any]]


class CommandHandler(ABCCommandHandler):
    """default command argument. Split args by `shlex.split` function and cast type from function annotations"""

    def __init__(
        self,
        tokenizer: Callable[[str], List[str]] = TokensParser(),
        caster: Optional[Callable[[Callable, List[str]], ARGS_AND_KWARGS]] = CommandArgumentsCaster(),
    ):
        self.tokenizer = tokenizer
        self.caster = caster

    def handle(self, fn: Callable[..., Any], text: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        arguments = self.tokenizer(text)
        return self.caster(fn, arguments) if self.caster else (tuple(arguments), {})

    def __call__(self, fn: Callable[..., Any], text: str):
        return self.handle(fn, text)


class RawCommandHandler(CommandHandler):
    """disable arguments parse and return raw string"""

    def __init__(self, tokenizer=TokensParserRaw(), caster=None):
        super().__init__(tokenizer, caster)
