from eggella import Eggella

app = Eggella(__name__)


@app.on_command("0echo")
def echo(*args):
    """print all passed arguments"""
    return " ".join(str(arg) for arg in args)

if __name__ == '__main__':
    app.loop()
