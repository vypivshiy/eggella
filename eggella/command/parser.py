import shlex
from typing import List

from eggella.command.abc import ABCCommandParser


class CommandParser(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return shlex.split(raw_command)


class CommandParserRaw(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return [raw_command]
