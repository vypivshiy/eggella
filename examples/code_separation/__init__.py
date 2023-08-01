from examples.code_separation.commands import *

# config file should be last imported
from examples.code_separation.config import app as APP
from examples.code_separation.events import *
from examples.code_separation.form import *

__all__ = ["APP"]


if __name__ == '__main__':
    APP.loop()
