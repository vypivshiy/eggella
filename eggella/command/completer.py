from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Union

from prompt_toolkit.completion import Completer, Completion, WordCompleter
from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.completion.nested import NestedDict
from prompt_toolkit.document import Document

from eggella.exceptions import CommandNotFoundError

if TYPE_CHECKING:
    from eggella.manager import CommandManager


class NestedCommandCompleter(Completer):
    """Modification Nested completer with meta information"""

    def __init__(
        self, options: Dict[str, Union[Completer, None]], ignore_case: bool = True, meta: Optional[Dict] = None
    ) -> None:
        self.options = options
        self.meta = meta or {}
        self.ignore_case = ignore_case

    def __repr__(self) -> str:
        return f"NestedCommandCompleter({self.options!r}, {self.meta!r} ignore_case={self.ignore_case!r})"

    @classmethod
    def from_nested_dict(cls, data: NestedDict, meta: Optional[Dict[str, str]] = None) -> "NestedCommandCompleter":
        options: Dict[str, Union[Completer, None]] = {}
        meta = meta or {}
        for key, value in data.items():
            if isinstance(value, Completer):
                options[key] = value
            elif isinstance(value, dict):
                options[key] = cls.from_nested_dict(value, meta)
            elif isinstance(value, set):
                options[key] = cls.from_nested_dict({item: None for item in value}, meta)
            else:
                assert value is None
                options[key] = None
        return cls(options=options, meta=meta)

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # If there is a space, check for the first term, and use a
        # subcompleter.
        if " " in text:
            first_term = text.split()[0]
            completer = self.options.get(first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                yield from completer.get_completions(new_document, complete_event)

        # No space in the input: behave exactly like `WordCompleter`.
        else:
            completer = WordCompleter(list(self.options.keys()), ignore_case=self.ignore_case, meta_dict=self.meta)
            yield from completer.get_completions(document, complete_event)


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
        if all(isinstance(d, dict) for d in completions):
            try:
                nested, meta = completions
                yield from NestedCommandCompleter.from_nested_dict(nested, meta).get_completions(
                    document, complete_event
                )
            except (ValueError, TypeError):  # unpack err
                yield
        else:
            # echo({'echo': None}, {})
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
        if command_obj.nested_completions:
            return command_obj.nested_completions, command_obj.nested_meta
        elif command_obj:
            return [command_obj.completion]
