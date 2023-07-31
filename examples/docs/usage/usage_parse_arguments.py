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
        return a / b
    except ZeroDivisionError:
        return "ZeroDivisionError"


# this build-in function, need set key
@app.on_command("sum")
def sum_(*digits: int):
    """sum all passed digits"""
    return sum(digits)


if __name__ == '__main__':
    app.loop()
