# Eggella
[ENG](README.md) [RU](README_RU.md)
> [Eggella](https://en.wikipedia.org/wiki/Eggella)  щитовой вулкан на Камчатке. Расположен на западной 
> оси Срединного хребта, на междуречье рек Эггелла и Чавыча

----
## Описание

Eggella - фреймворк для легкого написания консольных REPL приложений. 

API интерфейс вдохновлен проектом [vulcano](https://github.com/dgarana/vulcano), flask и различными чат-бот фреймворками
и основан на [prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

## Особенности

- Python 3.8+
- Аргументы для команд автоматически приводятся на основе аннотаций типов  
- Кросс-платформенность ([prompt-toolkit гарантирует(https://github.com/prompt-toolkit/python-prompt-toolkit#prompt_toolkit-features))
- FSM (конечные автоматы) для организации веточной логики
- Обработка ошибок
- Кастомизация событий
- Автоматическое создание автодополнения команд
- автоматическое создания help, man команд

## Установка

```shell
pip install eggella
```

## Hello world
```python
from eggella import Eggella


app = Eggella(__name__)


@app.on_command("hello")
def hello():
    return "Hello, world!"


if __name__ == '__main__':
    app.loop()
```

![quickstart](docs/gifs/hello_world.gif)

Смотрите [документацию](https://eggella.readthedocs.io/en/latest/) и [примеры](examples)!