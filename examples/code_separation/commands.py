from examples.code_separation.config import app


@app.on_error(ValueError, TypeError)
def on_sum_error(*_, **__):
    print("ERROR! WRONG ARGUMENTS")


@app.on_command("hello")
def hello():
    """print hello msg"""
    if not app.CTX.get("NAME"):
        print("type form for change this command output!")
        print("Hello, world!")
    print(f"Hello, {app.CTX.get('NAME')}!")


@on_sum_error
@app.on_command("sum")
def sum_(*args: int):
    """sum all passed digits"""
    return sum(args)
