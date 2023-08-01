from eggella import Eggella
app_cmd = Eggella("commands")


@app_cmd.on_error(ValueError, TypeError)
def on_sum_error(*_, **__):
    print("ERROR! WRONG ARGUMENTS")


@app_cmd.on_command("hello")
def hello():
    """print hello msg"""
    if not app_cmd.CTX.get("NAME"):
        print("type form for change this command output!")
        return "Hello, world!"
    return f"Hello, {app_cmd.CTX.get('NAME')}!"


@on_sum_error
@app_cmd.on_command("sum")
def sum_(*args: int):
    """sum all passed digits"""
    return sum(args)
