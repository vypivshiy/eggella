from eggella import Eggella

app = Eggella(__name__)
app.documentation = """Welcome to simple application
    this app does nothing

"""


@app.on_startup()
def startup_event():
    print("Hello! this quick Eggella app example!")
    print("Press Ctrl+C or Ctrl+D or type `exit` for close application")


@app.on_close()
def close_event():
    print("Goodbye! :D")


@app.on_command()
def hello():
    return "Hello, world!"


@app.on_error(ValueError, TypeError)
# first argument - command key, second - handled exception
def my_error_handler(key: str, exc: BaseException, *args: str, **kwargs: str):
    if key == "sum":
        bad_args = [arg for arg in args if not str(arg).isdigit()]
        print("Error! sum accept bad arguments:", *bad_args)
        return
    print(exc)


@app.on_error(ConnectionError)
def dummy_handle_exc(key: str, exc: BaseException, *args, **kwargs):
    print("catch connection error")
    return ":P"


@my_error_handler
@app.on_command("sum")
def sum_(*args: int):
    """sum all passed digits. if argument is not str - print error message"""
    return sum(args)


@my_error_handler
@app.on_command("raise-err1")
def raise_err1():
    """raise TypeError and catch exception"""
    raise TypeError("TypeError - my_error_handler catch this")


@dummy_handle_exc
@app.on_command("raise-err2")
def raise_err2():
    """raise ConnectionError and catch exception"""

    raise ConnectionError("connect error - dummy_handle_exc catch this")


@dummy_handle_exc  # decorators stack not work
@my_error_handler
@app.on_command("raise-err3")
def raise_err3():
    """raise TypeError and close app"""
    raise ConnectionError("connect error - dummy_handle_exc not catch this :(")


if __name__ == '__main__':
    app.loop()
