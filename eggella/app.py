from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Literal,
    Optional,
    Type,
    Union,
    overload,
)

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.completion.nested import NestedDict

from eggella._patches import FuzzyCompleter
from eggella._types import ARGS_AND_KWARGS, LITERAL_EVENTS, PromptLikeMsg
from eggella.command.abc import ABCCommandHandler
from eggella.command.objects import Command
from eggella.events.events import OnCommandRuntimeError
from eggella.exceptions import (
    CommandArgumentValueError,
    CommandNotFoundError,
    CommandParseError,
    CommandRuntimeError,
    CommandTooManyArgumentsError,
)
from eggella.fsm.fsm import FsmController, IntStateGroup
from eggella.manager import BlueprintManager, CommandManager, EventManager
from eggella.shortcuts.cmd_shortcuts import CmdShortCuts

_DEFAULT_INTRO_MSG = HTML(
    "<ansired>Press |CTRL+C| or |CTRL+D| or type</ansired> exit <ansired>for close this app</ansired>\n"
    "<ansigreen>Press |TAB| or type</ansigreen> help <ansigreen>for get commands information</ansigreen>"
)


class Eggella:
    __app_instances__: Dict[str, "Eggella"] = {}

    def __new__(cls, app_name: str, msg: PromptLikeMsg = "> ") -> "Eggella":
        if _app := cls.__app_instances__.get(app_name):
            return _app

        new_app = super().__new__(cls)
        cls.__app_instances__[app_name] = new_app
        return new_app

    def __init__(self, app_name: str, msg: PromptLikeMsg = "> "):
        self.app_name = app_name
        self.prompt_msg = msg
        self.session: PromptSession = PromptSession(msg)
        self.cmd = CmdShortCuts()

        # app context storage
        self.CTX: Dict[Hashable, Any] = {}
        # config
        self._intro: Union[HTML, PromptLikeMsg] = _DEFAULT_INTRO_MSG
        self._doc: str = ""
        self.overwrite_commands_from_blueprints: bool = False

        # managers
        self._command_manager: CommandManager = CommandManager(self)
        self._event_manager = EventManager(self)
        self._blueprint_manager = BlueprintManager(self)

        # fsm
        self.fsm = FsmController(self)

    @property
    def blueprint_manager(self):
        """Get blueprint manager"""
        return self._blueprint_manager

    @property
    def command_manager(self) -> CommandManager:
        """Get command manager"""
        return self._command_manager

    @property
    def event_manager(self) -> EventManager:
        """Get event manager"""
        return self._event_manager

    @property
    def documentation(self):
        """Get full manual text for help render"""
        return self._doc

    @documentation.setter
    def documentation(self, text: str):
        self._doc = text

    @property
    def intro(self):
        """startup intro text"""
        return self._intro

    @intro.setter
    def intro(self, text: Union[HTML, PromptLikeMsg]):
        self._intro = text

    def on_startup(self):
        """Register event manager on startup app"""
        return self.event_manager.startup()

    def on_close(self):
        """Register event manager on close app"""
        return self.event_manager.close()

    def on_error(self, *errors: Type[BaseException]):
        """Create error handler

        :param errors: types of Exceptions to be handled
        """
        return self.command_manager.on_error(*errors)

    def on_command(
        self,
        key: Optional[str] = None,
        short_description: Optional[str] = None,
        *,
        usage: Optional[str] = None,
        cmd_handler: Optional[Callable[[Callable[..., Any], str], ARGS_AND_KWARGS]] = None,
        nested_completions: Optional[NestedDict] = None,
        nested_meta: Optional[Dict[str, Any]] = None,
        is_visible: bool = True,
    ):
        """Register command

        :param key: command key. if not set - set key as function name
        :param short_description: short description
        :param usage: usage example
        :param cmd_handler: Command handler
        :param nested_completions: nested completer
        :param nested_meta: nested meta information
        :param is_visible: set visible command
        """
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
        """register state handler

        :param state: IntStateGroup state
        """
        return self.fsm.state(state)

    def register_states(self, states: Type[IntStateGroup]):
        """Register group states in this application

        :param states: IntStateGroup class
        :return:
        """
        self.fsm.attach(states)

    def register_blueprint(self, *apps: "Eggella"):
        """register blueprint for extension. Add on_startup, on_close, on_command, on_state events

        :param apps: Eggella applications
        :return:
        """
        self.blueprint_manager.register_blueprints(*apps)

    def _load_blueprints(self):
        self.blueprint_manager.load_blueprints()

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
        """Register command from function"""
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
        name: LITERAL_EVENTS,
        func: Optional[Callable],
    ) -> None:
        self._event_manager.register_event(name, func)

    def has_command(self, key: str) -> bool:
        """return True if command is registered

        :param key: command key
        :return:
        """
        return bool(self.command_manager.commands.get(key, None))

    def remove_command(self, key: str):
        """remove command from this application. raise KeyError, if command not founded

        :param key: command key
        :return:
        """
        if self.has_command(key):
            self.command_manager.commands.pop(key)
        else:
            raise KeyError

    def loop(self):
        """Run this application"""
        self.cmd.print_ft(self.intro)
        self._load_blueprints()
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
        """get command object from command_manager"""
        return self.command_manager.get(key)

    def _handle_error(self, key, args, exc):
        try:
            raise exc
        except CommandNotFoundError:
            self.event_manager.command_not_found_event(key, args)
            if self.event_manager.command_suggest_event:
                self.event_manager.command_suggest_event(
                    key, [c.key for c in self._command_manager.commands.values() if c.is_visible]
                )
        except CommandRuntimeError as exc:
            self.event_manager.command_runtime_err_event(key, args, exc)
        except CommandParseError:
            self.event_manager.command_error_event(key, args)
        except CommandTooManyArgumentsError as exc:
            self.event_manager.command_many_args_err_event(key, args, exc)
        except CommandArgumentValueError as exc:
            self.event_manager.command_argument_value_err_event(key, args, exc)

    def _handle_commands(self):
        """application loop"""
        while True:
            try:
                # if FSM activated - handle this
                if self.fsm.is_active():
                    # handle fsm events
                    try:
                        self.fsm.current()
                        continue
                    except KeyboardInterrupt:
                        if self.event_manager.fsm_kb_interrupt_event():
                            self.fsm.finish()
                    except EOFError:
                        if self.event_manager.fsm_eof_error_event():
                            self.fsm.finish()
                # handle main app input
                completer = FuzzyCompleter(completer=self.command_manager.get_completer())
                result = self.session.prompt(self.prompt_msg, completer=completer)
                if not result:
                    continue

                if (tokens := result.split(" ", 1)) and len(tokens) == 1:
                    key, args = tokens[0], ""
                else:
                    key, args = tokens[0], tokens[1]
                # handle input command
                if result := self.command_manager.exec(key, args):
                    self.event_manager.command_complete_event(result)
            # exit exceptions
            except KeyboardInterrupt:
                if self.event_manager.kb_interrupt_event():
                    break
            except EOFError:
                if self.event_manager.eof_event():
                    break
            # command errors handle
            except Exception as exc:
                self._handle_error(key, args, exc)
