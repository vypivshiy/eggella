from typing import Optional

from prompt_toolkit.validation import Validator

from eggella import EgellaApp
from eggella.fsm import IntState


class LoginForm(IntState):
    EMAIL = 0
    PASSWORD = 1
    ACCEPT = 2


# prompt validators

password_validator = Validator.from_callable(lambda s: len(s) > 6, error_message="password len should be bigger than 6")

email_validator = Validator.from_callable(lambda s: "@" in s, error_message="email is not valid")


app = EgellaApp(__name__)
app.register_states(LoginForm)


@app.on_command("auth")
def auth(email: Optional[str] = None, password: Optional[str] = None):
    """auth to service.

    if email and password not passed - invoke interactive auth
    """
    if email and password:
        print("Success auth!")
        print("Email:", email)
        print("Password:", "*" * len(password))
    else:
        app.fsm.run(LoginForm)


@app.on_state(LoginForm.EMAIL)
def email():
    app.fsm.ctx["email"] = app.cmd.prompt("Enter email > ", validator=email_validator)
    app.fsm.next()


@app.on_state(LoginForm.PASSWORD)
def password():
    # alias from prompt_toolkit.prompt functon
    app.fsm.ctx["password"] = app.cmd.prompt("Enter password > ", is_password=True, validator=password_validator)
    app.fsm.next()


@app.on_state(LoginForm.ACCEPT)
def finish():
    auth(app.fsm["email"], app.fsm["password"])
    # need close FSM
    app.fsm.finish()


if __name__ == '__main__':
    app.loop()
