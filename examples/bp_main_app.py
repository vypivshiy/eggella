import bp_plugins

from eggella import Eggella

app = Eggella(__name__)
app.register_blueprint(bp_plugins.bp1, bp_plugins.bp2)


if __name__ == '__main__':
    app.loop()
