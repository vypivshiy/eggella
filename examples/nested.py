from eggella import Eggella
from eggella.command import RawCommandHandler

app = Eggella(__name__)


@app.on_command(
    "config",
    cmd_handler=RawCommandHandler(),
    nested_completions={
        "proxy": {
            "socks": {"socks5://", "socks4://"},
            "http": {"https://", "http://"},
        },
        "timeout": {"0", "30", "60"},
        "render": {"spam", "egg", "foobar"},
    },
    nested_meta={
        "proxy": "set proxy",
        "socks": "usage SOCKS4/5 protocol",
        "http": "usage http(s) protocol",
        "timeout": "set request timeout",
        "render": "render a string object",
        "spam": "spammmm object",
        "egg": "wow! eggs!",
        "foobar": "rly? :O",
    },
)
def config(query: str):
    app.cmd.print_ft(f"Your answer: {query}")


if __name__ == '__main__':
    app.loop()
