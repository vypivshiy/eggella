from typing import TYPE_CHECKING, List

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.document import Document

from eggella.exceptions import CommandNotFoundError

if TYPE_CHECKING:
    from eggella.manager import CommandManager


class CommandCompleter(Completer):
    def __init__(self, manager: "CommandManager", ignore_case: bool = True):
        self.manager = manager
        self.ignore_case = ignore_case

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        text_before_cursor = document.text_before_cursor
        if self.ignore_case:
            text_before_cursor = text_before_cursor.lower()
        text_arr = text_before_cursor.split(" ")
        last_words = text_arr[-1]
        completions = self.__get_current_completions(text_arr[:-1])

        for completion, meta in completions:
            if completion not in document.text_before_cursor and "=" not in last_words:
                yield Completion(completion, -len(last_words), display_meta=meta or "")

    def __get_current_completions(self, text_arr: List[str]):
        if not text_arr:
            return self.manager.all_completions
        command = text_arr[0]
        try:
            command_obj = self.manager.get(command)
        except CommandNotFoundError:
            return []
        if command_obj:
            return [command_obj.completion]
