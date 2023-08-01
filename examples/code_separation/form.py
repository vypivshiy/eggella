from prompt_toolkit import HTML

from eggella.fsm import IntStateGroup
from examples.code_separation.config import app


class States(IntStateGroup):
    FIRST = 0
    LAST = 1
    AGE = 2
    RESULT = 3


app.register_states(States)


@app.on_command("form")
def form():
    """fill out a form"""
    app.cmd.print_ft("Start out a form")
    app.fsm.run(States)


@app.on_state(States.FIRST)
def first():
    app.cmd.print_ft("Enter first name")
    result = app.cmd.prompt("> ")
    app.fsm["first_name"] = result
    app.fsm.next()


@app.on_state(States.LAST)
def last():
    app.cmd.print_ft("Enter last name or `..` for back step")
    result = app.cmd.prompt("> ")
    if result == "..":
        return app.fsm.prev()
    app.fsm["last_name"] = result
    app.fsm.next()


@app.on_state(States.AGE)
def age():
    app.cmd.print_ft("Enter age or `..` for back step")
    result = app.cmd.prompt("> ")
    if result == "..":
        return app.fsm.prev()
    app.fsm["age"] = result
    app.fsm.next()


@app.on_state(States.RESULT)
def result():
    app.cmd.print_ft("Your answer:")
    app.cmd.print_ft("First name:", HTML(f"<ansired>{app.fsm['first_name']}</ansired>"))
    app.cmd.print_ft("Last name:", HTML(f"<ansigreen>{app.fsm['last_name']}</ansigreen>"))
    app.cmd.print_ft("Age:", HTML(f"<ansiyellow>{app.fsm['age']}</ansiyellow>"))
    # save to main app storage this information
    app.CTX["NAME"] = f"{app.fsm['first_name']} {app.fsm['last_name']} ({app.fsm['age']})"
    app.fsm.finish()
