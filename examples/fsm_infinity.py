from eggella import Eggella
from eggella.fsm import IntStateGroup


class States(IntStateGroup):
    ONE = 1


app = Eggella(__name__)
app.register_states(States)


@app.on_command()
def run_states():
    app.fsm.run(States)


@app.on_state(States.ONE)
def inf_state():
    app.cmd.print_ft("/-inf state! Type q for exit from state")
    result = app.cmd.prompt("\> ")
    if result == "q":
        app.fsm.finish()


if __name__ == '__main__':
    app.loop()
