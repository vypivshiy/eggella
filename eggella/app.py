from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.completion.fuzzy_completer import FuzzyCompleter
from prompt_toolkit.completion.nested import NestedDict
from prompt_toolkit.formatted_text import FormattedText

from eggella.command.abc import ABCCommandHandler
from eggella.command.objects import Command
from eggella.exceptions import (
    CommandArgumentValueError,
    CommandNotFoundError,
    CommandParseError,
    CommandTooManyArgumentsError,
)
from eggella.fsm.fsm import FsmController, IntStateGroup
from eggella.manager import CommandManager, EventManager
from eggella.shortcuts.cmd_shortcuts import CmdShortCuts

PromptLikeMsg = Union[str, FormattedText, Callable[..., Union[FormattedText, List[Tuple[str, str]]]]]

_DEFAULT_INTRO_MSG = HTML(
    "<ansired>Press |CTRL+C| or |CTRL+D| or type</ansired> exit <ansired>for close this app</ansired>\n"
    "<ansigreen>Press |TAB| or type</ansigreen> help <ansigreen>for get commands information</ansigreen>"
)


class Eggella:
    __app_instances__: Dict[str, "Eggella"] = {}

    def __new__(cls, app_name: str, msg: PromptLikeMsg = "~> ") -> "Eggella":
        if _app := cls.__app_instances__.get(app_name):
            return _app

        new_app = super().__new__(cls)
        cls.__app_instances__[app_name] = new_app
        return new_app

    def __init__(self, app_name: str, msg: PromptLikeMsg = "~> "):
        self.app_name = app_name
        self.prompt_msg = msg
        self.session: PromptSession = PromptSession(msg)
        self.cmd = CmdShortCuts()

        self.CTX: Dict[Hashable, Any] = {}
        self._intro: Union[HTML, PromptLikeMsg] = _DEFAULT_INTRO_MSG
        self._doc: str = ""
        # managers
        self._command_manager: CommandManager = CommandManager(self)
        self._event_manager = EventManager(self)

        # fsm
        self.fsm = FsmController(self)

    @property
    def documentation(self):
        return self._doc

    @documentation.setter
    def documentation(self, text: str):
        self._doc = text

    @property
    def intro(self):
        return self._intro

    @intro.setter
    def intro(self, text: Union[HTML, PromptLikeMsg]):
        self._intro = text

    def on_startup(self):
        return self._event_manager.startup()

    def on_close(self):
        return self._event_manager.close()

    def on_error(self, *errors: Type[BaseException]):
        return self._command_manager.on_error(*errors)

    def on_command(
        self,
        key: Optional[str] = None,
        short_description: Optional[str] = None,
        *,
        usage: Optional[str] = None,
        cmd_handler: Optional[ABCCommandHandler] = None,
        nested_completions: Optional[NestedDict] = None,
        nested_meta: Optional[Dict[str, Any]] = None,
        is_visible: bool = True,
    ):
        return self._command_manager.command(
            key,
            short_description=short_description,
            usage=usage,
            cmd_handler=cmd_handler,
            nested_completions=nested_completions,
            nested_meta=nested_meta,
            is_visible=is_visible,
        )

    def on_state(self, state: IntStateGroup):
        return self.fsm.state(state)

    def register_states(self, states: Type[IntStateGroup]):
        self.fsm.attach(states)

    def register_command(
        self,
        func: Callable,
        key: Optional[str] = None,
        short_description: Optional[str] = None,
        *,
        is_visible: bool = True,
        usage: Optional[str] = None,
        cmd_handler: Optional[ABCCommandHandler] = None,
    ):
        self._command_manager.register_command(
            func, key, short_description=short_description, usage=usage, cmd_handler=cmd_handler, is_visible=is_visible
        )

    @overload
    def register_event(
        self,
        name: Literal["start", "close", "kb_interrupt", "eof", "command_not_found", "command_complete"],
        func: Callable,
    ) -> None:
        pass

    @overload
    def register_event(
        self,
        name: Literal["command_suggest"],
        func: Optional[Callable],
    ) -> None:
        pass

    def register_event(
        self,
        name: Literal[
            "start", "close", "kb_interrupt", "eof", "command_not_found", "command_complete", "command_suggest"
        ],
        func: Optional[Callable],
    ) -> None:
        self._event_manager.register_event(name, func)

    def has_command(self, key: str) -> bool:
        return bool(self._command_manager.commands.get(key, None))

    def remove_command(self, key: str):
        if self.has_command(key):
            self._command_manager.commands.pop(key)
        else:
            raise KeyError

    def loop(self):
        self.cmd.print_ft(self.intro)
        self._command_manager.register_buildin_commands()
        self._handle_startup_events()
        self._handle_commands()
        self._handle_close_events()

    def _handle_startup_events(self):
        for event in self._event_manager.startup_events:
            event()

    def _handle_close_events(self):
        for event in self._event_manager.close_events:
            event()

    def get_command(self, key: str) -> Command:
        return self._command_manager.get(key)

    def _handle_commands(self):
        while True:
            try:
                completer = FuzzyCompleter(completer=self._command_manager.get_completer())
                result = self.session.prompt(self.prompt_msg, completer=completer)
                if not result:
                    continue

                if (tokens := result.split(" ", 1)) and len(tokens) == 1:
                    key = tokens[0]
                    args = ""
                else:
                    key, args = tokens[0], tokens[1]

                if result := self._command_manager.exec(key, args):
                    self._event_manager.command_complete_event(result)
            except CommandNotFoundError:
                self._event_manager.command_not_found_event(key, args)
                self._event_manager.command_suggest_event(
                    key, [c.key for c in self._command_manager.commands.values() if c.is_visible]
                )
            except CommandParseError:
                self._event_manager.command_error_event(key, args)
            except CommandTooManyArgumentsError as exc:
                self._event_manager.command_many_args_err_event(key, args, exc)
            except CommandArgumentValueError as exc:
                self._event_manager.command_argument_value_err_event(key, args, exc)
            except KeyboardInterrupt:
                if self._event_manager.kb_interrupt_event():
                    break
            except EOFError:
                if self._event_manager.eof_event():
                    break
