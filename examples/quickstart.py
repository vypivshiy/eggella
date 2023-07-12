from eggella import EgellaApp

app = EgellaApp(__name__)


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


@app.on_command("sum")
def sum_(*args: int):
    return sum(args)


if __name__ == '__main__':
    app.loop()
    