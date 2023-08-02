from eggella import Eggella

app_events = Eggella("events")


@app_events.on_startup()
def intro():
    print("Hello! this startup event!")


@app_events.on_close()
def close_event():
    print("This close event! Goodbye!")
