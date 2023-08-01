from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from eggella import Eggella

from commands import app_cmd
from events import app_events
from form import app_form


app = Eggella("demo app", "# ")
# set first epilog documentation
app.documentation = """Demo app
This demo application
"""
# prompt session config
app.session = PromptSession("# ", complete_style=CompleteStyle.MULTI_COLUMN)
# preload variables to app storage
app.CTX["Variable"] = True
app.register_blueprint(
    app_events,
    app_cmd,
    app_form
)
