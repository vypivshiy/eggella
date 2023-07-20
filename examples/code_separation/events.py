from examples.code_separation.config import app


@app.on_startup()
def intro():
    print("Hello! this startup event!")


@app.on_close()
def close_event():
    print("This close event! Goodbye!")
