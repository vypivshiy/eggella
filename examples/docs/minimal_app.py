from eggella import Eggella

app = Eggella(__name__)


@app.on_startup()
def startup():
    print("Hello! This my first application!")


@app.on_close()
def close():
    print("Goodbye!")


@app.on_command()
def echo(*args: str):
    return " ".join(args)


if __name__ == '__main__':
    app.loop()