import shlex
import warnings
from typing import List

from eggella.command.abc import ABCTokensParser


class TokensParser(ABCTokensParser):
    """Default tokens parser. Split input string arguments by `shlex.split` function"""

    def __call__(self, raw_command: str) -> List[str]:
        return shlex.split(raw_command)


class TokensParserRaw(ABCTokensParser):
    """Tokens split input string to arguments"""

    def __call__(self, raw_command: str) -> List[str]:
        return [raw_command]


class CommandParser(TokensParser):
    def __init__(self):
        warnings.warn(
            "CommandParser has deprecated, please use `TokenParser` instead", stacklevel=3, category=DeprecationWarning
        )


class CommandParserRaw(TokensParserRaw):
    def __init__(self):
        warnings.warn(
            "CommandParserRaw has deprecated, please use `TokenParserRaw` instead",
            stacklevel=3,
            category=DeprecationWarning,
        )
