# Minimal app

This is an example of a simple application where the 
`echo` command will duplicate all arguments passed. 

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



Program description:

- `Eggella` - main class application, register all commands and events 
- `@app.on_startup()` - register startup events
- `@app.on_close()` - register on close app events (on invoke `exit` or press CTRL+C)
- `@app.on_command()` - register commands
- `app.loop()` - start application method 
