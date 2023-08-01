from eggella import Eggella

from bp_plugins import bp1, bp2

app = Eggella(__name__)
app.register_blueprint(bp1, bp2)


if __name__ == '__main__':
    app.loop()
