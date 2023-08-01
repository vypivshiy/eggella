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
)

from prompt_toolkit.completion.nested import NestedDict

from eggella.command.abc import ABCCommandHandler
from eggella.command.completer import CommandCompleter
from eggella.command.handler import CommandHandler
from eggella.command.objects import Command
from eggella.events.events import (
    OnCommandArgumentValueError,
    OnCommandCompleteSuccess,
    OnCommandError,
    OnCommandNotFound,
    OnCommandTooManyArgumentsError,
    OnEOFError,
    OnKeyboardInterrupt,
    OnSuggest,
)
from eggella.exceptions import (
    CommandArgumentValueError,
    CommandNotFoundError,
    CommandTooManyArgumentsError,
)
from eggella.shortcuts.help_pager import gen_help_pager

if TYPE_CHECKING:
    from eggella.app import Eggella


_ErrorEventsMapping = Dict[str, Tuple[Type[BaseException], ...]]


class CommandManager:
    def __init__(self, app: "Eggella"):
        self._app = app
        self.commands: Dict[str, Command] = {}
        self.error_events: Dict[str, Callable[[str, BaseException, str, str], Any]] = {}
        self.handled_exceptions: _ErrorEventsMapping = {}

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
        command = self.get(key)

        if not command.is_visible:
            raise CommandNotFoundError

        try:
            return command.handle(args)
        except TypeError as e:
            if 'too many positional arguments' in e.args[0]:
                raise CommandTooManyArgumentsError("Too many arguments") from e
            else:
                raise e
        except ValueError as e:
            raise CommandArgumentValueError(f"Wrong argument type passed: {e.args}") from e
        except BaseException as e:
            if err_handler := self.error_events.get(command.fn.__name__):
                handle_exceptions = self.handled_exceptions.get(command.fn.__name__, None)
                if handle_exceptions and any(e.__class__ == exc for exc in handle_exceptions):
                    _args, _kwargs = self._simple_parse_arguments(args)
                    return err_handler(key, e, *_args, **_kwargs)
                else:
                    raise e
            raise e

    def get_completer(self) -> CommandCompleter:
        return CommandCompleter(self)  # type: ignore

    def on_error(self, *errors: Type[BaseException]):
        def decorator(handler: Callable[[str, BaseException, str, str], Any]):
            @wraps(handler)
            def decorator_wrapper(func: Callable[..., Any]):
                if not self.error_events.get(func.__name__):
                    self.error_events[func.__name__] = handler
                    self.handled_exceptions[func.__name__] = errors

                @wraps(func)
                def wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except BaseException as e:
                        if any(e.__class__ == exc for exc in errors):
                            return handler("", e, *args, **kwargs)
                        raise e

                return wrapper

            return decorator_wrapper

        return decorator

    @property
    def all_completions(self) -> List[Tuple[str, str]]:
        return [com.completion for com in self.commands.values() if com.is_visible]

    def get(self, key: str) -> Command:
        if command := self.commands.get(key, None):
            return command
        raise CommandNotFoundError(f"Command {key} not founded")

    def command(
        self,
        key: Optional[str] = None,
        *,
        short_description: Optional[str] = None,
        usage: Optional[str] = None,
        cmd_handler: Optional[ABCCommandHandler] = None,
        nested_completions: Optional[NestedDict] = None,
        nested_meta: Optional[Dict[str, Any]] = None,
        is_visible: bool = True,
    ):
        def decorator(func: Callable):
            self.register_command(
                func,
                key=key,
                short_description=short_description,
                usage=usage,
                cmd_handler=cmd_handler,
                nested_completions=nested_completions,
                nested_meta=nested_meta,
                is_visible=is_visible,
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
        nested_completions: Optional[NestedDict] = None,
        nested_meta: Optional[Dict[str, Any]] = None,
        is_visible: bool = True,
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
                nested_completions={key: nested_completions},
                nested_meta=nested_meta or {},
                is_visible=is_visible,
            )
        elif cmd_handler:
            self.commands[key] = Command(
                fn=func,
                key=key,
                handler=cmd_handler,
                short_description=short_description,
                usage=usage,
                nested_completions={key: nested_completions},
                nested_meta=nested_meta or {},
                is_visible=is_visible,
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

    def register_buildin_commands(self):
        self.register_command(self._exit_command, "exit")
        _nested_commands = {k: None for k in self.commands.keys()}
        _nested_meta = {}
        _nested_meta.update({k: v.short_desc for k, v in self.commands.items()})
        self.register_command(
            self._help_command,
            "help",
            usage="help; help exit",
            nested_completions=_nested_commands,
            nested_meta=_nested_meta,
        )


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
        self.command_many_args_err_event: Callable[..., None] = OnCommandTooManyArgumentsError()
        self.command_argument_value_err_event: Callable[..., None] = OnCommandArgumentValueError()

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
