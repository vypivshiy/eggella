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


if __name__ == '__main__':
    app.loop()
