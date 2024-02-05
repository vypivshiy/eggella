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
    Set,
    Tuple,
    Type,
)

from prompt_toolkit.completion.nested import NestedDict

from eggella._types import CALLABLE_ERR_HANDLER
from eggella.command.completer import CommandCompleter
from eggella.command.handler import CommandHandler
from eggella.command.objects import Command
from eggella.events.events import (
    OnCommandArgumentValueError,
    OnCommandCompleteSuccess,
    OnCommandError,
    OnCommandNotFound,
    OnCommandRuntimeError,
    OnCommandTooManyArgumentsError,
    OnEOFError,
    OnFSMEOFError,
    OnFSMKeyboardInterrupt,
    OnKeyboardInterrupt,
    OnSuggest,
)
from eggella.exceptions import (
    CommandArgumentValueError,
    CommandNotFoundError,
    CommandRuntimeError,
    CommandTooManyArgumentsError,
)
from eggella.shortcuts.help_pager import gen_help_commands, gen_man_pager

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
                raise CommandTooManyArgumentsError(e.args[0]) from e
            elif 'missing a required argument: ' in e.args[0]:
                raise CommandArgumentValueError(e.args[0]) from e
            else:
                msg = f"{e!r} in `{command.fn.__name__}` callable"
                raise CommandRuntimeError(msg) from e
        except ValueError as e:
            if e.args and 'invalid literal for' in e.args[0]:
                raise CommandArgumentValueError(e.args[0]) from e
            msg = f"{e!r} in `{command.fn.__name__}` callable"
            raise CommandRuntimeError(msg) from e
        except Exception as e:
            if err_handler := self.error_events.get(command.fn.__name__):
                handle_exceptions = self.handled_exceptions.get(command.fn.__name__, None)
                if handle_exceptions and any(e.__class__ == exc for exc in handle_exceptions):
                    _args, _kwargs = self._simple_parse_arguments(args)
                    return err_handler(key, e, *_args, **_kwargs)
                else:
                    msg = f"{e!r} in `{command.fn.__name__}` callable"
                    raise CommandRuntimeError(msg)
            msg = f"{e!r} in `{command.fn.__name__}` callable"
            raise CommandRuntimeError(msg)

    def get_completer(self) -> CommandCompleter:
        return CommandCompleter(self)  # type: ignore

    def on_error(self, *errors: Type[BaseException]):
        def decorator(handler: CALLABLE_ERR_HANDLER):
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
        cmd_handler: Optional[Callable[[Callable[..., Any], str], Tuple[Tuple[Any, ...], Dict[str, Any]]]] = None,
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
        cmd_handler: Optional[Callable[[Callable[..., Any], str], Tuple[Tuple[Any, ...], Dict[str, Any]]]] = None,
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
        else:
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
        """show help or print all available commands if not argument passed"""
        if not key:
            return gen_help_commands(self._app)
        elif comma := self.commands.get(key):
            return f"{key} {comma.command_description}"
        else:
            raise CommandNotFoundError

    def _man_page(self):
        """generate man page view with all commands"""
        gen_man_pager(self._app)

    @staticmethod
    def _exit_command():
        """exit from this application"""
        raise KeyboardInterrupt

    def register_buildin_commands(self):
        self.register_command(self._exit_command, "exit")
        self.register_command(self._man_page, ".man")

        # generate nested for help command
        _nested_commands = {k: None for k in self.commands.keys()}
        _nested_meta = {}
        _nested_meta.update({k: v.command_description for k, v in self.commands.items()})
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
        # TODO typing more accurately
        # loop events
        self.kb_interrupt_event: Callable[..., bool] = OnKeyboardInterrupt()
        self.eof_event: Callable[..., bool] = OnEOFError()
        # commands events
        self.command_error_event: Callable[..., None] = OnCommandError()
        self.command_not_found_event: Callable[..., None] = OnCommandNotFound()
        self.command_complete_event: Callable[..., None] = OnCommandCompleteSuccess()
        self.command_suggest_event: Optional[Callable[..., None]] = OnSuggest()
        self.command_many_args_err_event: Callable[..., None] = OnCommandTooManyArgumentsError()
        self.command_argument_value_err_event: Callable[..., None] = OnCommandArgumentValueError()
        self.command_runtime_err_event: Callable[..., None] = OnCommandRuntimeError()
        # FSM events
        self.fsm_kb_interrupt_event: Callable[..., bool] = OnFSMKeyboardInterrupt()
        self.fsm_eof_error_event: Callable[..., bool] = OnFSMEOFError()

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


class BlueprintManager:
    def __init__(self, main_app: "Eggella"):
        self.app = main_app

        self.blueprints: List["Eggella"] = []
        self._loaded_blueprints: Set[str] = set()

    def register_blueprints(self, *bp_apps: "Eggella"):
        for bp_app in bp_apps:
            self.blueprints.append(bp_app)

    def load_blueprints(self):
        for blueprint in self.blueprints:
            if blueprint.app_name in self._loaded_blueprints:
                continue
            # register commands to main app
            for key, command in blueprint.command_manager.commands.items():
                if self.app.command_manager.commands.get(key) and not self.app.overwrite_commands_from_blueprints:
                    raise TypeError(
                        f"Command '{key}' from blueprint `{blueprint.app_name}` already registered. "
                        f"For overwrite commands set `overwrite_commands_from_blueprints=True`"
                    )
                self.app.command_manager.commands[key] = command
            # register FSM groups to main app
            for key, fsm_state in blueprint.fsm.fsm_storage.items():
                self.app.fsm.fsm_storage[key] = fsm_state

            # register events
            for start_ev in blueprint.event_manager.startup_events:
                self.app.event_manager.startup_events.append(start_ev)

            for close_ev in blueprint.event_manager.close_events:
                self.app.event_manager.close_events.append(close_ev)

            self._loaded_blueprints.add(blueprint.app_name)
