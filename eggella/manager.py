import shlex
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)

from eggella.command.abc import ABCCommandHandler
from eggella.command.completer import CommandCompleter
from eggella.command.handler import CommandHandler
from eggella.command.objects import Command
from eggella.events.events import (
    OnCommandCompleteSuccess,
    OnCommandError,
    OnCommandNotFound,
    OnEOFError,
    OnKeyboardInterrupt,
    OnSuggest,
)
from eggella.exceptions import CommandNotFoundError
from eggella.shortcuts.help_pager import gen_help_pager

if TYPE_CHECKING:
    from eggella.app import Eggella


_ErrorEventsMapping = Dict[str, Tuple[Callable, Union[Type[BaseException], Tuple[Type[BaseException], ...]]]]


class CommandManager:
    def __init__(self, app: "Eggella"):
        self._app = app
        self.commands: Dict[str, Command] = {}
        self.error_handlers: Dict[str, Callable[..., Any]] = {}
        self._register_buildin_commands()

    @staticmethod
    def _simple_parse_arguments(raw_command: str) -> Tuple[Tuple[str, ...], Dict[str, str]]:
        tokens = shlex.split(raw_command)
        args: List[str] = []
        kwargs: Dict[str, str] = {}
        for token in tokens:
            if "=" in token:
                key, value = token.split("=", 1)
                kwargs[key] = value
            else:
                args.append(token)
        return tuple(args), kwargs

    def exec(self, key: str, args: str):
        if command := self.commands.get(key):
            try:
                return command.handle(args)
            except BaseException as e:
                if err_handler := self.error_handlers.get(command.fn.__name__):
                    _args, _kwargs = self._simple_parse_arguments(args)
                    return err_handler(key, e, *_args, **_kwargs)
                else:
                    raise e
        else:
            raise CommandNotFoundError("Command not founded")

    def get_completer(self) -> CommandCompleter:
        return CommandCompleter(self)  # type: ignore

    def on_error(self, errors: Union[Type[BaseException], Tuple[Type[BaseException], ...]]):
        def decorator(handler: Callable[..., Any]):
            @wraps(handler)
            def decorator_wrapper(func: Callable[..., Any]):
                if not self.error_handlers.get(func.__name__):
                    self.error_handlers[func.__name__] = handler

                @wraps(func)
                def wrapper(*args: Any, **kwargs: Dict[str, Any]):
                    try:
                        return func(*args, **kwargs)
                    except errors:
                        return handler(*args, **kwargs)

                return wrapper

            return decorator_wrapper

        return decorator

    @property
    def all_completions(self):
        return [com.completion for com in self.commands.values()]

    def get(self, key: str) -> Command:
        if comma := self.commands.get(key, None):
            return comma
        raise CommandNotFoundError(f"Command {key} not founded")

    def command(
        self,
        key: Optional[str] = None,
        *,
        short_description: Optional[str] = None,
        usage: Optional[str] = None,
        cmd_handler: Optional[ABCCommandHandler] = None,
    ):
        def decorator(func: Callable):
            self.register_command(
                func,
                key=key,
                short_description=short_description,
                usage=usage,
                cmd_handler=cmd_handler,
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def register_command(
        self,
        func: Callable,
        key: Optional[str] = None,
        *,
        short_description: Optional[str] = None,
        usage: Optional[str] = None,
        cmd_handler: Optional[ABCCommandHandler] = None,
    ):
        if not key:
            key = func.__name__
        if self.commands.get(key):
            raise TypeError(f"Command '{key}' already register")

        if not cmd_handler:
            self.commands[key] = Command(
                fn=func,
                key=key,
                handler=CommandHandler(),
                short_description=short_description,
                usage=usage,
            )
        elif cmd_handler:
            self.commands[key] = Command(
                fn=func,
                key=key,
                handler=cmd_handler,
                short_description=short_description,
                usage=usage,
            )

    def _help_command(self, key: Optional[str] = None):
        """show help or show pager documentation for all commands if not argument passed"""
        if not key:
            commands = self.commands.values()
            gen_help_pager(self._app, commands)
            return
        elif comma := self.commands.get(key):
            return f"{key} - {comma.short_desc}"
        else:
            raise CommandNotFoundError

    @staticmethod
    def _exit_command():
        """exit from this application"""
        raise KeyboardInterrupt

    def _register_buildin_commands(self):
        self.register_command(self._help_command, "help", usage="help; help exit")
        self.register_command(self._exit_command, "exit")


class EventManager:
    def __init__(self, app: "Eggella"):
        self.app = app
        self.startup_events: List[Callable] = []
        self.close_events: List[Callable] = []
        self.errors_events: Dict[str, Callable] = {}

        self.kb_interrupt_event: Callable[..., bool] = OnKeyboardInterrupt()
        self.eof_event: Callable[..., bool] = OnEOFError()
        self.command_error_event: Callable[..., None] = OnCommandError()
        self.command_not_found_event: Callable[..., None] = OnCommandNotFound()
        self.command_complete_event: Callable[..., None] = OnCommandCompleteSuccess()
        self.command_suggest_event: Optional[Callable[..., None]] = OnSuggest()

    def register_event(
        self,
        name: Literal[
            "start", "close", "kb_interrupt", "eof", "command_not_found", "command_complete", "command_suggest"
        ],
        func: Optional[Callable],
    ):
        if name == "start" and func:
            self.startup_events.append(func)
            return
        elif name == "close" and func:
            self.close_events.append(func)
            return
        elif name == "kb_interrupt" and func:
            self.kb_interrupt_event = func
            return
        elif name == "eof" and func:
            self.eof_event = func
            return
        elif name == "command_not_found" and func:
            self.command_not_found_event = func
            return
        elif name == "command_complete" and func:
            self.command_complete_event = func
            return
        elif name == "command_suggest":
            self.command_suggest_event = func
            return
        raise TypeError("Unknown event type")

    def startup(self):
        def decorator(func: Callable):
            self.register_event("start", func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def close(self):
        def decorator(func: Callable):
            self.register_event("close", func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator
