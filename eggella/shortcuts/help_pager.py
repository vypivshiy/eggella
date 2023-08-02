from typing import TYPE_CHECKING, Iterable

# https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/pager.py
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

if TYPE_CHECKING:
    from eggella import Eggella
    from eggella.command.objects import Command


def _render_man_text(app: "Eggella", commands: Iterable["Command"]):
    """
    {{APP DOCUMENTATION}}

    COMMANDS
       {{comma1}} - [arg1] [arg2] - {{short description}}
           {{description}}
           {{description}}
           {{description}}
       Usage:
           {{USAGE}}
           {{USAGE}}

       {{comma2}} - [arg1] [arg2] - {{short description}}
           {{description}}
           {{description}}
           {{description}}
       Usage:
           {{USAGE}}
           {{USAGE}}

       {{comma3}} - [arg1] [arg2] - {{short description}}
           {{description}}
           {{description}}
           {{description}}

    """

    text = app.documentation
    text += "\n"
    text += "COMMANDS:\n"
    for command in commands:
        args = " ".join([f"[{arg}]" for arg in command.arguments])
        text += f"    {command.key} {args}\n"
        if command.short_description:
            for line in command.short_description.split("\n"):
                text += f"        {line}\n"
        else:
            for line in command.docstring.split("\n"):
                text += f"        {line}\n"
        text += "\n"
        if command.usage:
            text += "        USAGE:\n"
            for line in command.usage.split("\n"):
                text += f"            {line}\n"
            text += "\n"
    return text


def gen_man_pager(app: "Eggella"):
    commands = app.command_manager.commands.values()
    text = _render_man_text(app, commands)
    search_field = SearchToolbar(text_if_not_searching=[("class:not-searching", "Press '/' to start searching.")])

    text_area = TextArea(
        text=text,
        read_only=True,
        scrollbar=True,
        search_field=search_field,
    )
    status_bar_text = [
        ("class:status", "Help page"),
        ("class:status", " - Press "),
        ("class:status.key", "Ctrl-C or Q"),
        ("class:status", " to exit, "),
        ("class:status.key", "/"),
        ("class:status", " for searching."),
    ]
    root_container = HSplit(
        [
            # The top toolbar.
            Window(
                content=FormattedTextControl(status_bar_text),  # type: ignore
                height=D.exact(1),
                style="class:status",
            ),
            # The main content.
            text_area,
            search_field,
        ]
    )

    # Key bindings.
    bindings = KeyBindings()

    @bindings.add("c-c")
    @bindings.add("q")
    def _(event):
        event.app.exit()

    style = Style.from_dict(
        {
            "status": "reverse",
            "status.position": "#aaaa00",
            "status.key": "#ffaa00",
            "not-searching": "#888888",
        }
    )

    # create application.
    application = Application(  # type: ignore
        layout=Layout(root_container, focused_element=text_area),
        key_bindings=bindings,
        enable_page_navigation_bindings=True,  # type: ignore
        mouse_support=True,
        style=style,
        full_screen=True,
    )
    application.run()


def gen_help_commands(app: "Eggella") -> str:
    text = ""
    commands = app.command_manager.commands.values()
    max_len_key = max(
        (f"{c.key} (" + ", ".join(f"{arg}" for arg in c.arguments) + ")" for c in commands if c.is_visible),
        key=len,
    )
    max_spacer_len = len(max_len_key) - 1

    for command in commands:
        if command.is_visible:
            args = "(" + ", ".join(f"{arg}" for arg in command.arguments) + ")" if command.arguments else ""
            spacer_len = max_spacer_len - len(command.key + args)
            text += f"{command.key} {args} {' ' * spacer_len} {command.get_short_description()}\n"
    return text
