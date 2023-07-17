import random

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import Validator

from eggella import Eggella
from eggella.fsm import IntStateGroup


class GameStates(IntStateGroup):
    GAME = 1
    WIN = 2
    LOSE = 3
    EXIT = 4
    RESTART = 5


NUMBER_VALIDATOR = Validator.from_callable(
    lambda s: s.isdigit() or s in ("q", "r"), error_message="Should be number or `q, r`"
)

app = Eggella(__name__)
app.register_states(GameStates)
app.CTX["stats"] = {"win": 0, "lose": 0}


@app.on_command(
    "start",
    usage="`start` or `start 0 10 2` or start start_num=5 end_num=10 attempts=2",
)
def start_game(start_num: int = 0, end_num: int = 10, attempts: int = 3):
    """start game. can configurate rules"""
    app.cmd.print_ft(f"Game config: minimal number={start_num}, max_number={end_num}, attempts={attempts}")
    app.cmd.print_ft(HTML("<seagreen>Start game:</seagreen>"))
    app.CTX["game"] = {
        "min": start_num,
        "max": end_num,
        "attempts": attempts,
        "digit": random.randint(start_num, end_num),
    }
    app.CTX["last_config"] = app.CTX["game"].copy()
    app.fsm.run(GameStates)


@app.on_command("stats")
def show_stats():
    """show game session stats"""
    win = app.CTX["stats"]["win"]
    lose = app.CTX["stats"]["lose"]
    app.cmd.print_ft(HTML(f"Wins: <ansigreen>{win}</ansigreen>\nDefeats: <ansired>{lose}</ansired>"))
    return


@app.on_state(GameStates.GAME)
def game():
    if app.CTX["game"]["attempts"] == 0:
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

    elif value < app.CTX["game"]["digit"]:
        app.CTX["game"]["attempts"] -= 1
        app.cmd.print_ft(HTML(f"Should be <ansired>bigger</ansired> than {value}"))
        return app.fsm.set(GameStates.GAME)

    elif value > app.CTX["game"]["digit"]:
        app.CTX["game"]["attempts"] -= 1
        app.cmd.print_ft(HTML(f"Should be <ansired>less</ansired> than {value}"))
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
        app.CTX["game"] = app.CTX["last_config"].copy()
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


if __name__ == "__main__":
    app.loop()
