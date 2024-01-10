from typing import Optional

from prompt_toolkit.validation import Validator

from eggella import Eggella
from eggella.fsm import IntStateGroup


class LoginForm(IntStateGroup):
    EMAIL = 0
    PASSWORD = 1
    ACCEPT = 2


# prompt validators
password_validator = Validator.from_callable(
    lambda s: len(s) > 6 or s == "..", error_message="password len should be bigger than 6"
)

email_validator = Validator.from_callable(lambda s: "@" in s or s == "..", error_message="email is not valid")

confirm_validator = Validator.from_callable(lambda s: s in {"y", "n"})


app = Eggella(__name__)
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
    result = app.cmd.prompt("Enter email > ", validator=email_validator)
    if result == "..":
        return app.fsm.finish()
    app.fsm.ctx["email"] = result
    app.fsm.next()


@app.on_state(LoginForm.PASSWORD)
def password():
    # alias from prompt_toolkit.prompt functon
    result = app.cmd.prompt("Enter password > ", is_password=True, validator=password_validator)
    if result == "..":
        return app.fsm.prev()
    app.fsm.ctx["password"] = result
    app.fsm.next()


@app.on_state(LoginForm.ACCEPT)
def finish():
    print("Your input:")
    print("email:", app.fsm["email"])
    print("if correct, type `y` or `n` for back prev step")
    confirm = app.cmd.prompt("(y/n)> ", validator=confirm_validator)
    if confirm == "n":
        return app.fsm.prev()
    auth(app.fsm["email"], app.fsm["password"])
    # don't forget to close FSM!
    app.fsm.finish()


if __name__ == '__main__':
    app.loop()
