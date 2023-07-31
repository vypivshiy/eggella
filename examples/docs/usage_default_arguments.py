from eggella import Eggella

app = Eggella(__name__)


@app.on_command()
def hello(name: str = "Anon"):
    return f"Hello, {name}"


if __name__ == '__main__':
    app.loop()
