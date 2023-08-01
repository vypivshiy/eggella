from eggella import Eggella

app = Eggella(__name__, "$ ")


@app.on_command(is_visible=False)
def secret():
    return "Is secret command"


@app.on_command()
def admin():
    cmd = app.get_command("secret")
    cmd.is_visible = not cmd.is_visible
    app.prompt_msg = "# " if cmd.is_visible else "$ "


if __name__ == '__main__':
    app.loop()
