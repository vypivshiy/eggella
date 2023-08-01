from prompt_toolkit import HTML
from prompt_toolkit.validation import Validator

from eggella import Eggella

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
