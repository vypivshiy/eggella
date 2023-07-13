from difflib import SequenceMatcher
from typing import Any, Iterable

from prompt_toolkit import print_formatted_text as print_ft
from prompt_toolkit.formatted_text.html import HTML
from prompt_toolkit.shortcuts.prompt import confirm
from prompt_toolkit.styles import Style

from eggella.events.abc import ABCEvent


class OnStartup(ABCEvent):
    _STYLES = Style.from_dict({"help": "#80ff00", "close": "#ff0000", "cmd_key": "#7d7c80 italic"})

    def __call__(self):
        pass


class OnClose(ABCEvent):
    def __call__(self):
        pass


class OnKeyboardInterrupt(ABCEvent):
    def __call__(self) -> bool:
        try:
            if confirm("Exit?"):
                return True
        except (KeyboardInterrupt, EOFError):
            return True
        return False


class OnEOFError(ABCEvent):
    def __call__(self):
        try:
            if confirm("Exit?"):
                exit(0)
        except (KeyboardInterrupt, EOFError):
            exit(0)


class OnCommandError(ABCEvent):
    def __call__(self, key: str, inline_arguments: str):
        pass


class OnCommandNotFound(ABCEvent):
    _STYLE = Style.from_dict(
        {
            "cmd_key": "#7d7c80 italic",
        }
    )

    def __call__(self, key: str, inline_arguments: str):
        print_ft(
            HTML(f"<ansired>Error!</ansired> command <cmd_key>{key}</cmd_key> not founded"),
            style=self._STYLE,
        )


class OnSuggest(ABCEvent):
    _STYLE = Style.from_dict({"mean": "#ffff00 bold"})

    def __call__(self, command: str, possible_commands: Iterable[str]):
        suggested_command = None
        ratio = 0
        for possible_command in possible_commands:
            possible_ratio = SequenceMatcher(None, command, possible_command).ratio()
            if possible_ratio > ratio:
                ratio = possible_ratio  # type: ignore
                suggested_command = possible_command
        print_ft(
            HTML(f"Did your mean: <mean>{suggested_command}</mean> ?"),
            style=self._STYLE,
        )


class OnCommandCompleteSuccess(ABCEvent):
    _STYLE = Style.from_dict({"out": "#696969 bold"})

    def __call__(self, result: Any):
        if result:
            print_ft(HTML(f"<out>{result}</out>"), style=self._STYLE)


class OnCommandArgumentsException(ABCEvent):
    def __call__(self, key: str, error: BaseException, *args, **kwargs):
        pass
