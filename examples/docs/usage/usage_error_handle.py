from eggella import Eggella

app = Eggella(__name__)


@app.on_error(ZeroDivisionError)
def zero_div_err(*_, **__):
    return "ERROR! ZeroDivisionError"


@zero_div_err
@app.on_command()
def div(a: int, b: int):
    """div two digits"""
    return a / b


if __name__ == '__main__':
    app.loop()
