# Advanced
This section will describe finer application settings.

In most cases, prompt_toolkit will be used, to work with it, read the official
documentation for this library.

## Custom parser command arguments
```python
import re
from typing import List

from eggella import Eggella
from eggella.command import CommandHandler, RawCommandHandler
from eggella.command.abc import ABCCommandParser

app = Eggella(__name__)


class DigitParserOnly(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return re.findall(r"(\d+)", raw_command)


@app.on_command("to-upper", cmd_handler=RawCommandHandler())
def words_to_up(text: str):
    """convert input to upper case"""
    return text.upper()


@app.on_command("sum", cmd_handler=CommandHandler(parser=DigitParserOnly()))
def sum_(*args: int):
    """sum all digits. ignore all non digit symbols

    eg:
    ~> sum 192.168.0.1
    361
    """
    return sum(args)


if __name__ == '__main__':
    app.loop()
```
## Custom Application

### Сustom prompt message, PromptSession
```python
import os
from datetime import datetime
from random import choice
from string import hexdigits

from prompt_toolkit import PromptSession

# set custom title in terminal
from prompt_toolkit.shortcuts import set_title

from prompt_toolkit.shortcuts.prompt import CompleteStyle
# add command history feature 
from prompt_toolkit.history import FileHistory 

from eggella import Eggella


def get_prompt():
    """create dynamic cursor"""
    now = datetime.now()
    now_time = f"{now.hour:02}:{now.minute:02}:{now.second:02}"
    set_title(f"Demo Custom app app [{now_time}]")
    rand_color = "#" + "".join([choice(hexdigits) for _ in range(6)])
    return [
        (rand_color, f"[{os.getlogin()}] "),
        ("bg:#008800 #ffffff", f" {now.hour:02}:{now.minute:02}:{now.second:02}"),
        ("", " ~ "),
    ]

app = Eggella(__name__, get_prompt)
app.session = PromptSession(get_prompt, 
                            history=FileHistory(".history"),
                            complete_style=CompleteStyle.MULTI_COLUMN)

if __name__ == '__main__':
    app.loop()
```

### Remove commands
```python
from eggella import Eggella

app = Eggella(__name__)
app.remove_command("help")
app.remove_command("exit")


if __name__ == '__main__':
    app.loop()
```


### Events

- `"command_complete"` - the event of returning the result when executing the command (return).
It takes one argument, there can only be one in the application context and it is overwritten.

```python
from typing import Any

from eggella import Eggella

app = Eggella(__name__)

def result_output(result: Any):
    print(f"Your result `{result}` meow ^.^")

app.register_event("command_complete", result_output)

@app.on_command("sum")
def sum_(*digits: int):
    return sum(digits)


if __name__ == '__main__':
    app.loop()
```


- "command_suggest" - event when the command is incorrectly typed. The default searches for "similar".
It accepts the entered command and the list of available commands and there can only be one in the application context and it is overwritten.


```python
from eggella import Eggella

app = Eggella(__name__)

def my_suggest(failed_comma: str, commands: list[str]):
    print(f"Error! command {failed_comma} not founded")
    print("Available commands:", commands)

    
app.register_event("command_suggest", my_suggest)

if __name__ == '__main__':
    app.loop()
```


- "eof" - `EOFError` error event (ctrl + D)
Takes no arguments, there can be one in the application context

```python
from eggella import Eggella

app = Eggella(__name__)


# exit from app immediately, ignore on_close events
app.register_event("eof", lambda: exit(1))

if __name__ == '__main__':
    app.loop()
```

- "kb_interrupt" - event when `KeyboardInterrupt` error is raised
Takes no arguments, there can be one in the application context

> Builtin command `exit` throw `KeyboardInterrupt` exception
