import inspect
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

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
    def arguments(self) -> List[str]:
        args = inspect.signature(self.fn).parameters.values()
        return [str(arg) for arg in args]

    @property
    def docstring(self) -> str:
        return inspect.getdoc(self.fn) or ""

    @property
    def short_desc(self):
        arg_list = " ".join(f"[{arg}]" for arg in self.arguments)
        if self.short_description:
            return f"({arg_list}) - {self.short_description}"
        elif self.docstring:
            short_desc = self.docstring.split("\n")[0]
            return f"{arg_list} - {short_desc}"
        return f"{arg_list}"

    @property
    def completion(self) -> Tuple[str, str]:
        return self.key, self.short_desc

    @property
    def help(self):
        arg_list = " ".join(f"[{arg}]" for arg in self.arguments)
        if len(self.docstring.split("\n")) > 1:
            if self.usage:
                return f"      {self.key} ({arg_list})\n            {self.docstring}\nUSAGE:\n      {self.usage}"
            return f"      {self.key} ({arg_list})\n            {self.docstring}"
        if self.usage:
            return f"      {self.key} ({arg_list}) - {self.docstring}\nUSAGE:\n      {self.usage}"
        return f"      {self.key} ({arg_list}) - {self.docstring}"
