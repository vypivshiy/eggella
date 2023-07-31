from eggella import Eggella
from eggella.command import RawCommandHandler

app = Eggella(__name__)


@app.on_command(cmd_handler=RawCommandHandler())
def echo(command: str):
    return command


if __name__ == '__main__':
    app.loop()
