from eggella import Eggella

app = Eggella(__name__)


@app.on_command()
def set_name(name: str):
    """Set name"""
    app.CTX["name"] = name


@app.on_command()
def hello():
    if name := app.CTX.get("name"):
        return f"Hello, {name}"
    return "Hello, Anon!"


if __name__ == '__main__':
    app.loop()
