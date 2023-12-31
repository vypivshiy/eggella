import random

from prompt_toolkit import HTML
from prompt_toolkit.validation import Validator

from eggella import Eggella
from eggella.fsm import IntStateGroup


class GameStates(IntStateGroup):
    GAME = 1
    WIN = 2
    LOSE = 3
    EXIT = 4
    RESTART = 5


app = Eggella("Guess game")
app.register_states(GameStates)

NUMBER_VALIDATOR = Validator.from_callable(
    lambda s: s.isdigit() or s in ("q", "r"), error_message="Should be number or `q, r`"
)

# game stats
app.CTX["stats"] = {"win": 0, "lose": 0}


@app.on_command()
def start(start_num: int = 0, end_num: int = 10, attempts: int = 3):
    """Start guess game"""
    print(f"Game configuration: numbers range: {start_num}-{end_num} attempts: {attempts}")
    app.CTX["game"] = {
        "num_range": (start_num, end_num),
        "attempts_cfg": attempts,
        "attempts": attempts,
        "digit": random.randint(start_num, end_num),
    }
    app.fsm.run(GameStates)


@app.on_state(GameStates.GAME)
def game():
    if app.CTX["game"]["attempts"] == 0:
        print("You lose!")
        return app.fsm.set(GameStates.LOSE)

    count = app.CTX["game"]["attempts"]
    value = app.cmd.prompt(f"[{count}]Enter number -> ", validator=NUMBER_VALIDATOR)
    if value == "q":
        return app.fsm.set(GameStates.EXIT)
    elif value == "r":
        return app.fsm.set(GameStates.RESTART)

    value = int(value)

    if value == app.CTX["game"]["digit"]:
        return app.fsm.set(GameStates.WIN)
    elif value > app.CTX["game"]["digit"]:
        app.CTX["game"]["attempts"] -= 1
        app.cmd.print_ft(HTML("<ansired>Input should be less</ansired>"))
        return app.fsm.set(GameStates.GAME)
    else:
        app.CTX["game"]["attempts"] -= 1
        app.cmd.print_ft(HTML("<ansired>Input should be bigger</ansired>"))
        return app.fsm.set(GameStates.GAME)


@app.on_state(GameStates.EXIT)
def _exit_game():
    if app.cmd.confirm("Exit from game? You will be credited with defeat"):
        app.cmd.print_ft(HTML("<ansired>Manual exit game, Defeated</ansired>"))
        app.CTX["stats"]["lose"] += 1
        return app.fsm.finish()
    return app.fsm.set(GameStates.GAME)


@app.on_state(GameStates.RESTART)
def _restart_game():
    if app.cmd.confirm("Restart game? You will be credited with defeat"):
        app.cmd.print_ft(HTML("<ansired>Restart game, Defeated</ansired>"))
        app.CTX["stats"]["lose"] += 1
        app.CTX["game"]["digit"] = random.randint(*app.CTX["game"]["num_range"])
        app.CTX["game"]["attempts"] = app.CTX["game"]["attempts_cfg"]
        return app.fsm.set(GameStates.GAME)
    return app.fsm.set(GameStates.GAME)


@app.on_state(GameStates.LOSE)
def _lose_game():
    app.cmd.prompt(HTML(f"<ansired>Defeated</ansired> Correct answer {app.CTX['game']['digit']}"))
    app.CTX["stats"]["lose"] += 1
    return app.fsm.finish()


@app.fsm.state(GameStates.WIN)
def _win_game():
    app.cmd.prompt(HTML("<ansigreen>Winner winner, chicken dinner!</ansigreen>"))
    app.CTX["stats"]["win"] += 1
    return app.fsm.finish()


@app.on_command("stats")
def show_stats():
    """show game session stats"""
    win = app.CTX["stats"]["win"]
    lose = app.CTX["stats"]["lose"]
    app.cmd.print_ft(HTML(f"Wins: <ansigreen>{win}</ansigreen>\nDefeats: <ansired>{lose}</ansired>"))
    return


if __name__ == '__main__':
    app.loop()
