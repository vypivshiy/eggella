import re
from typing import List

from eggella import EgellaApp
from eggella.command import CommandHandler, CommandParserRaw
from eggella.command.command import ABCCommandParser

app = EgellaApp(__name__)


class DigitParserOnly(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return re.findall(r"(\d+)", raw_command)


@app.on_command("to-upper", cmd_handler=CommandHandler(parser=CommandParserRaw(), caster=None))
def words_to_up(text: str):
    """convert input to upper case"""
    return text.upper()


@app.on_command("sum", cmd_handler=CommandHandler(parser=DigitParserOnly()))
def sum_(*args: int):
    """sum all digits. ignore all symbols

    eg:
    ~> sum 192.168.0.1
    361
    """
    return sum(args)


if __name__ == '__main__':
    app.loop()
