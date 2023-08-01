from eggella import Eggella

from prompt_toolkit import HTML

from eggella.fsm import IntStateGroup


app_form = Eggella("forms")


class States(IntStateGroup):
    FIRST = 0
    LAST = 1
    AGE = 2
    RESULT = 3


app_form.register_states(States)


@app_form.on_command("form")
def form():
    """fill out a form"""
    app_form.cmd.print_ft("Start out a form")
    app_form.fsm.run(States)


@app_form.on_state(States.FIRST)
def first():
    app_form.cmd.print_ft("Enter first name")
    result = app_form.cmd.prompt("> ")
    app_form.fsm["first_name"] = result
    app_form.fsm.next()


@app_form.on_state(States.LAST)
def last():
    app_form.cmd.print_ft("Enter last name or `..` for back step")
    result = app_form.cmd.prompt("> ")
    if result == "..":
        return app_form.fsm.prev()
    app_form.fsm["last_name"] = result
    app_form.fsm.next()


@app_form.on_state(States.AGE)
def age():
    app_form.cmd.print_ft("Enter age or `..` for back step")
    result = app_form.cmd.prompt("> ")
    if result == "..":
        return app_form.fsm.prev()
    app_form.fsm["age"] = result
    app_form.fsm.next()


@app_form.on_state(States.RESULT)
def result():
    app_form.cmd.print_ft("Your answer:")
    app_form.cmd.print_ft("First name:", HTML(f"<ansired>{app_form.fsm['first_name']}</ansired>"))
    app_form.cmd.print_ft("Last name:", HTML(f"<ansigreen>{app_form.fsm['last_name']}</ansigreen>"))
    app_form.cmd.print_ft("Age:", HTML(f"<ansiyellow>{app_form.fsm['age']}</ansiyellow>"))
    # save to main app storage this information
    app_form.CTX["NAME"] = f"{app_form.fsm['first_name']} {app_form.fsm['last_name']} ({app_form.fsm['age']})"
    app_form.fsm.finish()
