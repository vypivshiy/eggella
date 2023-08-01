from eggella import Eggella

# all app instances should be unique name
bp1 = Eggella("plugin 1")
bp2 = Eggella("plugin 2")

__all__ = ["bp1", "bp2"]


@bp1.on_startup()
def plugin_loaded():
    print("Plugin 1 loaded")


@bp1.on_command("plugin_1")
def cmd1():
    """this command from bp1 instance"""
    return "Plugin 1 command"


@bp2.on_startup()
def plugin_loaded2():
    print("Plugin 2 loaded")


@bp2.on_command("plugin_2")
def cmd2():
    """this command from bp2 instance"""
    return "Plugin 2 command"
