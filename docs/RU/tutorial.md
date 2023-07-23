# Tutorial
В этом туториале мы напишем игру "guess game" (угадай число).

## Prepare
Сначала определимся с планом проекта:

1. При команде `start` игра запускается. Игра должна конфигурироваться: 
   - устанавливаться диапазон чисел (минимальное и максимальное)
   - число попыток
2. Игра генерирует случайное число в заданном диапазоне и игра запускается
3. Если игрок вводит число меньше сгенерированного - уведомляет
4. Если игрок вводит число больше сгенерированного - уведомляет
5. Если попытки закончились - вывести сообщение о поражении
6. Если игрок угадал число - вывести сообщение о победе и выйти в главное меню
7. Вести статистику побед и поражений (выводить с помощью команды `stats`)

> Дополнительно: вы можете сохранять статистику игры в json файл, например

Схема проекта:
```
    start (start_num: int, end_num: int, attemps: int)
          |
          v
      Generate number (<digit>)
          |
          v
        Guess game (<attemps>)
           |
           v
          Input()
             |
     True    V      False       
    ----- Correct?  ---------
    |                       |
    v               True    v           False
  Increase win     ------<attemps> == 0? -------
   counter         |                           |
                   |                   True    |                   False
                Increase              -------Bigger than <digit>? -----
                Draw counter          |                               |
                                      v                               v
                                    print                            print 
                                      |                               |
                                      v                               v
                                    decrease                       decrease
                                    attempts                       attempts
                                      |                                |
                                      v                                V
                                   GOTO Input()                    GOTO Input() 
```             

## Start coding
Добавим состояния и логику работы. Предварительные настройки запишем в `app.CTX`:
```python
import random

from eggella import Eggella
from eggella.fsm import IntStateGroup

app = Eggella("Guess game")


class GameStates(IntStateGroup):
    GAME = 1


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
```

Минимально игра готова, но есть проблемы:
1. Нет валидации ввода числа
2. Не реализована статистика
3. prompt_toolkit позволяет делать более красивый вывод

Добавим [валидатор](https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#input-validation)
и подсчёт статистики. 
Также, дополнительно для примера будет добавлен предварительный выход из игры и рестарт.

```python
import random

from prompt_toolkit.validation import Validator
from prompt_toolkit import HTML

from eggella import Eggella
from eggella.fsm import IntStateGroup

app = Eggella("Guess game")
NUMBER_VALIDATOR = Validator.from_callable(
    lambda s: s.isdigit() or s in ("q", "r"), error_message="Should be number or `q, r`"
)

# game stats
app.CTX["stats"] = {"win": 0, "lose": 0}


class GameStates(IntStateGroup):
    GAME = 1
    WIN = 2
    LOSE = 3
    EXIT = 4
    RESTART = 5


@app.on_command()
def start(start_num: int = 0, end_num: int = 10, attempts: int = 3):
    """Start guess game"""
    print(f"Game configuration: numbers range: {start_num}-{end_num} attempts: {attempts}")
    app.CTX["game"] = {
        "num_range": (start_num, end_num),
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
```

И раз уж есть nested completer, можно дополнительно улучшить подсказки для запуска игры:

```python
import random

from prompt_toolkit.validation import Validator
from prompt_toolkit import HTML

from eggella import Eggella
from eggella.fsm import IntStateGroup

app = Eggella("Guess game")
NUMBER_VALIDATOR = Validator.from_callable(
    lambda s: s.isdigit() or s in ("q", "r"), error_message="Should be number or `q, r`"
)

# game stats
app.CTX["stats"] = {"win": 0, "lose": 0}


class GameStates(IntStateGroup):
    GAME = 1
    WIN = 2
    LOSE = 3
    EXIT = 4
    RESTART = 5


@app.on_command(
    nested_completions={"start_num=0": {"end_num=10": {"attempts=2": None}}},
    nested_meta={
        "start_num=0": "first number in range",
        "end_num=10": "last number in range",
        "attempts=2": "number of attempts"})
def start(start_num: int = 0, end_num: int = 10, attempts: int = 3):
    """Start guess game"""
    print(f"Game configuration: numbers range: {start_num}-{end_num} attempts: {attempts}")
    app.CTX["game"] = {
        "num_range": (start_num, end_num),
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
```
