import random

from eggella import Eggella
from eggella.fsm import IntStateGroup


class GameStates(IntStateGroup):
    GAME = 1


app = Eggella("Guess game")
app.register_states(GameStates)


@app.on_command()
def start(start_num: int = 0, end_num: int = 10, attempts: int = 3):
    """Start guess game"""
    print(f"Game configuration: numbers range: {start_num}-{end_num} attempts: {attempts}")
    app.CTX["game"] = {
        "attempts": attempts,
        "digit": random.randint(start_num, end_num),
    }
    app.fsm.run(GameStates)


@app.on_state(GameStates.GAME)
def game():
    if app.CTX["game"]["attempts"] == 0:
        print("You lose!")
        return app.fsm.finish()

    count = app.CTX["game"]["attempts"]
    value = app.cmd.prompt(f"[{count}]Enter number -> ")
    value = int(value)

    if value == app.CTX["game"]["digit"]:
        print("You win!")
        return app.fsm.finish()
    elif value > app.CTX["game"]["digit"]:
        app.CTX["game"]["attempts"]-=1
        print("Input should be less")
        return app.fsm.set(GameStates.GAME)
    else:
        app.CTX["game"]["attempts"]-=1
        print("Input should be bigger")
        return app.fsm.set(GameStates.GAME)


if __name__ == '__main__':
    app.loop()
