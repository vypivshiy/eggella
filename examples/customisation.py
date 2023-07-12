# TODO typing better all events
import os
from datetime import datetime
from random import choice

from prompt_toolkit.shortcuts import set_title

from eggella import EgellaApp

from string import hexdigits


def get_prompt():
    """create dynamic cursor"""
    now = datetime.now()
    now_time = f"{now.hour:02}:{now.minute:02}:{now.second:02}"
    set_title(f"Demo Custom app app [{now_time}]")
    rand_color = "#" + "".join([choice(hexdigits) for _ in range(6)])
    return [
        (rand_color, f"[{os.getlogin()}] "),
        ("bg:#008800 #ffffff", f" {now.hour:02}:{now.minute:02}:{now.second:02}"),
        ("", " ~ ")
    ]


def result_output(result):
    print(f"Your output: {result}, meow ^^")


app = EgellaApp(__name__, msg=get_prompt)
app.intro = "my custom startup intro!"
# or set custom PromptSession object
app.session.refresh_interval = .5

# TODO implement all decorators
app.register_event("start", lambda: print("new startup event"))
app.register_event("command_complete", result_output)
app.register_event("eof", lambda: exit(1))  # exit from app immediately, ignore close events
app.register_event("command_suggest", lambda a, b: None)  # disable command_suggest feature


@app.on_command()
def test():
    """return test123"""
    return "test123"


@app.on_command()
def test_2():
    """return 1234, 'spam egg'"""
    return 1234, "spam egg"


if __name__ == '__main__':
    app.loop()
    # new startup event
    # ~> test
    # Your output: test123, meow ^^
    # ~> test_2
    # Your output: (1234, 'spam egg'), meow ^^
    # ~>
