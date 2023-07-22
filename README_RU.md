# Eggella
[ENG](README.md) [RU](README_RU.md)
> [Eggella](https://en.wikipedia.org/wiki/Eggella)  щитовой вулкан на Камчатке. Расположен на западной 
> оси Срединного хребта, на междуречье рек Эггелла и Чавыча

----
## Описание

Eggella - фреймоворк для легкого написания консольных REPL приложений. 

API интерфейс вдохновлен проектом [vulcano](https://github.com/dgarana/vulcano) и различными чат-бот фреймворками
и основан на [prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

## Особенности

- Python 3.8+
- Аргументы для команд автоматически приводятся на основе аннотаций типов  
- Кросс-платформенность (prompt-toolkit гарантирует)
- FSM (конечные автоматы) для организации веточной логики
- Обработка ошибок
- Кастомизация событий
- Автоматическое создание комманд комплитер
- автоматическое создания описание комманд через help (как в unix `man` команда)
## Установка

`pip install eggella`
## Примеры:
### Hello world
```python
from eggella import Eggella


app = Eggella(__name__)


@app.on_command("hello")
def hello():
    return "Hello, world!"


if __name__ == '__main__':
    app.loop()
```

### Basic
```python
from eggella import Eggella

app = Eggella(__name__)


@app.on_startup()
def startup_event():
    print("Hello! this quick Eggella app example!")


@app.on_close()
def close_event():
    print("Goodbye! :D")


@app.on_command()
def hello():
    return "Hello, world!"


@app.on_command("sum")
def sum_(*args: int):
    return sum(args)


if __name__ == '__main__':
    app.loop()
```
### FSM example

```python
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
    lambda s: len(s) > 6,
    error_message="password len should be bigger than 6")

email_validator = Validator.from_callable(
    lambda s: "@" in s,
    error_message="email is not valid")

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
```

## Documentation
TODO