import inspect
from typing import Any, Callable, Dict, NamedTuple, Optional, Tuple

from eggella.command.abc import ABCCommandHandler
from eggella.command.handler import CommandHandler


class Command(NamedTuple):
    fn: Callable[..., Any]
    key: str
    handler: ABCCommandHandler = CommandHandler()
    usage: Optional[str] = None
    short_description: Optional[str] = None

    def handle(self, command_text: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        args, kwargs = self.handler.handle(self.fn, command_text)
        return self.fn(*args, **kwargs)

    @property
    def short_desc(self):
        args = inspect.signature(self.fn).parameters.values()
        arg_list = ", ".join(str(arg) for arg in args)
        docstring = inspect.getdoc(self.fn) or ""
        if self.short_description:
            return f"({arg_list}) - {self.short_description}"
        elif docstring:
            short_desc = docstring.split("\n")[0]
            return f"({arg_list}) - {short_desc}"
        return f"({arg_list})"

    @property
    def completion(self):
        return self.key, self.short_desc

    @property
    def help(self):
        args = inspect.signature(self.fn).parameters.values()
        arg_list = ", ".join(str(arg) for arg in args)
        docstring = inspect.getdoc(self.fn) or ""
        if len(docstring.split("\n")) > 1:
            if self.usage:
                return f"{self.key} ({arg_list})\n\t{docstring}\nUSAGE:\n\t{self.usage}"
            return f"{self.key} ({arg_list})\n\t{docstring}"
        if self.usage:
            f"{self.key} ({arg_list}) - {docstring}\n\tUSAGE:\n{self.usage}"
        return f"{self.key} ({arg_list}) - {docstring}"
