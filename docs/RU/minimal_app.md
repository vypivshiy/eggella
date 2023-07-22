# Minimal app

Это пример простого приложения, где команда `echo` будет дублировать все переданные аргументы. 

> example.py
```python
from eggella import Eggella

app = Eggella(__name__)


@app.on_startup()
def startup():
    print("Hello! This my first application!")

    
@app.on_close()
def close():
    print("Goodbye!")
    
    
@app.on_command()
def echo(*args):
    return " ".join(args)

if __name__ == '__main__':
    app.loop()
```

Запускать командой `python example.py`. Чтобы вывести все доступные команды, нажмите `Tab`.

Разбор программы:
- `Eggella` - основной класс приложения, через которое регистрируются команды и события 
- `@app.on_startup()` - декоратор регистрации события, которое сработает при первом запуске приложения
- `@app.on_close()` - декоратор регистрации события, которое сработает при закрытии приложения. Срабатывает
при вызове команды `exit` или нажатием `CTRL+C`
- `@app.on_command()` - декоратор регистрации команды.
- `app.loop()` - метод запуска программы
