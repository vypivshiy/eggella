import os
import sys
from typing import Callable

from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.shortcuts.prompt import confirm


class CmdShortCuts:
    @property
    def prompt(self) -> Callable:
        return prompt

    @property
    def print_ft(self) -> Callable:
        return print_formatted_text

    @property
    def confirm(self) -> Callable:
        return confirm

    @staticmethod
    def clear() -> None:
        os.system("cls") if sys.platform == "win32" else os.system("clear")
