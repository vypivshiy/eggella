import os
import sys
from typing import Callable, Union

from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts.prompt import PromptSession, confirm

E = KeyPressEvent


def create_confirm_session_2(
    message: str,
    suffix: str = " ([y]/n) ",
    default_key: Union[str, Keys] = Keys.Enter,
    default_value: bool = True,
) -> PromptSession[bool]:
    bindings = KeyBindings()

    @bindings.add("y")
    @bindings.add("Y")
    def yes(event: E) -> None:
        session.default_buffer.text = "y"
        event.app.exit(result=True)

    @bindings.add("д")
    @bindings.add("Д")
    def yes_cyrillic(event: E) -> None:
        session.default_buffer.text = "д"
        event.app.exit(result=True)

    @bindings.add("n")
    @bindings.add("N")
    def no(event: E) -> None:
        session.default_buffer.text = "n"
        event.app.exit(result=False)

    @bindings.add("н")
    @bindings.add("Н")
    def no_cyrillic(event: E) -> None:
        session.default_buffer.text = "н"
        event.app.exit(result=False)

    @bindings.add(default_key)
    def _default(event: E) -> None:
        event.app.exit(result=default_value)

    @bindings.add(Keys.Any)
    def _(__: E) -> None:
        pass

    complete_message = merge_formatted_text([message, suffix])
    session: PromptSession[bool] = PromptSession(complete_message, key_bindings=bindings)
    return session


def yes_no_exit(message: str = "Do you really want to exit?"):
    return create_confirm_session_2(message).prompt()


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
