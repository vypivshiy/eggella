# Usage
Framework usage description:

## Events
You can set events on application start or close.
These events can be useful, for example, when configuring an application.

These events take no arguments and return nothing.

```python
from eggella import Eggella

app = Eggella(__name__)

@app.on_startup()
def startup_1():
    print("startup 1")


@app.on_startup()
def startup_2():
    print("startup 2")

# These events activate if double press CTRL+C or type `exit` command

@app.on_close()
def close_1():
    print("close event 1")


@app.on_close()
def close_2():
    print("close event 2")
```

## Set key, add description
By default, the command key is taken from the name of the function being decorated. 
If the key needs to be remapped - pass the first key argument.

To add a description of a command, you can pass the `short_description` parameter, or add
docstring at the beginning of the function:

```python
from eggella import Eggella

app = Eggella(__name__)


@app.on_command("0echo")
def echo(*args):
    """print all passed arguments"""
    return " ".join(args)

if __name__ == '__main__':
    app.loop()
```

## Parse arguments
By default, keys are parsed using the built-in library [shlex](https://docs.python.org/3/library/shlex.html?highlight=shlex#shlex.split)
and converted to annotation-based types:

```python
from eggella import Eggella

app = Eggella(__name__)


@app.on_command()
def hello(name: str):
    """print hello {name}"""
    return f"hello, {name}"

@app.on_command()
def div(a: int, b: int):
    """sum two digits"""
    try:
        return a/b
    except ZeroDivisionError:
        return "ZeroDivisionError"

    
# this build-in function, need set key
@app.on_command("sum")  
def sum_(*digits: int):
    """sum all passed digits"""
    return sum(digits)

if __name__ == '__main__':
    app.loop()
```

> You can also pass arguments in named form, EG `hello name="Georgiy"`

> In `sum` and `div`, when passing a non-numeric argument, the program will crash with an error.
> This page will address this question in the [Error handle](#error-handle) section.

## Default arguments
You can set default value(s):

```python
from eggella import Eggella

app = Eggella(__name__)


@app.on_command()
def hello(name: str = "Anon"):
    return f"Hello, {name}"

```
> If you don't pass a name parameter, it will default to `"Anon"`

## Custom parse arguments handler
In some cases, the standard argument handler may not be suitable.

You can use build-in `RawCommandHandler` - ignores argument tokenization and type casting
passes the entire string to the function.

```python
from eggella import Eggella
from eggella.command import RawCommandHandler

app = Eggella(__name__)


@app.on_command(cmd_handler=RawCommandHandler())
def echo(command: str):
    return command


if __name__ == '__main__':
    app.loop()
```

Command handler customization will be in the `Advanced` section

## Nested completer
If additional command hints and descriptions are needed:

> In `nested_meta` for correct meta output, keys should be unique.

```python
from eggella import Eggella
from eggella.command import RawCommandHandler

app = Eggella(__name__)


@app.on_command(
    cmd_handler=RawCommandHandler(),
    nested_completions={
        "proxy": {
            "socks": {"socks5://", "socks4://"},
            "http": {"https://", "http://"},
        },
        "timeout": {"0", "30", "60"},
        "render": {"spam", "egg", "foobar"},
    },
    nested_meta={
        "proxy": "set proxy",
        "socks": "usage SOCKS4/5 protocol",
        "http": "usage http(s) protocol",
        "timeout": "set request timeout",
        "render": "render a string object",
        "spam": "spammmm object",
        "egg": "wow! eggs!",
        "foobar": "rly? :O",
    },
)
def config(query: str):
    return f"Your answer: {query}"


if __name__ == '__main__':
    app.loop()
```

## Error handle

In the [Parse arguments](#parse-arguments) section, when passing a non-numeric argument to commands
`sum` and `div` - the program crashes with an error. You can create an error handler for such situations:
```python
from eggella import Eggella

app = Eggella(__name__)

@app.on_error(TypeError, ValueError)
def non_digit_handle(*_, **__):
    return "ERROR! detect non digit argument"

@non_digit_handle
@app.on_command()
def div(a: int, b: int):
    """sum two digits"""
    try:
        return a/b
    except ZeroDivisionError:
        return "ZeroDivisionError"

    
@non_digit_handle
@app.on_command("sum")  
def sum_(*digits: int):
    """sum all passed digits"""
    return sum(digits)


if __name__ == '__main__':
    app.loop()
```

## App storage
You can storage variables in `app.CTX` storage (it's a standard python dict)
```python
from eggella import Eggella

app = Eggella(__name__)

@app.on_command()
def set_name(name: str):
    """Set name"""
    app.CTX["name"] = name

    
@app.on_command()
def hello():
    if name := app.CTX.get("name"):
        return f"Hello, {name}"
    return "Hello, Anon!"
```
## Shortcuts
The application has aliases of some methods to reduce the number of imports from `prompt_toolkit`
and they are stored in `Eggella.cmd`

```python
from eggella import Eggella

from prompt_toolkit import HTML
from prompt_toolkit.validation import Validator
app = Eggella(__name__)


@app.on_command()
def color():
    """print red colored text"""
    # alias prompt_toolkit.print_formatted_text
    app.cmd.print_ft(HTML("<ancired>RED TEXT</ancired>"))

    
@app.on_command()
def digit_input():
    """invoke prompt_toolkit.prompt function"""
    # alias prompt_toolkit.prompt
    ans = app.cmd.prompt(">>> ", validator=Validator.from_callable(lambda s: s.isdigit()))
    return f"Your answer: {ans}"

@app.on_command()
def clear():
    """clear terminal output. If windows - invoke `cls`. Unix - `clear`"""
    app.cmd.clear()

    
if __name__ == '__main__':
    app.loop()
```

## FSM
FSM aka [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine)
designed to simplify the organization of the "branch" logic of the program.

```python
from typing import Optional

from prompt_toolkit.validation import Validator

from eggella import Eggella
from eggella.fsm import IntStateGroup


class LoginForm(IntStateGroup):
    EMAIL = 0
    PASSWORD = 1
    ACCEPT = 2


# prompt validators
password_validator = Validator.from_callable(lambda s: len(s) > 6, error_message="password len should be bigger than 6")

email_validator = Validator.from_callable(lambda s: "@" in s, error_message="email is not valid")


app = Eggella(__name__)
app.register_states(LoginForm)


@app.on_command("auth")
def auth(email: Optional[str] = None, password: Optional[str] = None):
    """auth to service. If email and password not passed - invoke interactive auth"""
    if email and password:
        print("Success auth!")
        print("Email:", email)
        print("Password:", "*" * len(password))
    else:
        app.fsm.run(LoginForm)


@app.on_state(LoginForm.EMAIL)
def email():
    app.fsm.ctx["email"] = app.cmd.prompt("Enter email > ", validator=email_validator)
    app.fsm.next()


@app.on_state(LoginForm.PASSWORD)
def password():
    app.fsm.ctx["password"] = app.cmd.prompt("Enter password > ", is_password=True, validator=password_validator)
    app.fsm.next()


@app.on_state(LoginForm.ACCEPT)
def finish():
    auth(app.fsm["email"], app.fsm["password"])
    # need close FSM
    app.fsm.finish()


if __name__ == '__main__':
    app.loop()
```

Program description:

To add FSM you nedd:
- Declare a class by inheriting Enum class `IntStateGroup`
- Register this state group class using `app.register_states(...)`
- Usage `on_state(<IntStates.num>)` to call function given a state.

- IntStateGroup - IntEnum class.

Methods:
- `app.fsm` - access to manager FSM states
- `app.fsm.run(<IntStates>)` - Run FSM in first state
- `app.fsm.start(<IntStates.num>)` - Run FSM from a given state
- `app.fsm.next()` - Move to the next state. If this is the last state - calls `finish`.
- `app.fsm.prev()` - Move to the prev state. If this is the first state - calls `finish`.
- `app.fsm.set(<IntStates.num>)` - Move to a given state
- `app.fsm[<key>]` - FSM storage access (get, set)
- `app.fsm.finish()` - Close FSM. **All written values in the FSM storage are deleted automatically.**
