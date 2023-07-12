import ast
import inspect
import shlex
from contextlib import suppress
from typing import Any, Callable, Dict, List, Tuple

from eggella.command.abc import ABCCommandArgumentsCaster, ABCCommandParser
from eggella.tools.type_caster import TypeCaster


class CommandParser(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return shlex.split(raw_command)


class CommandParserRaw(ABCCommandParser):
    def __call__(self, raw_command: str) -> List[str]:
        return [raw_command]


class CommandArgumentsCaster(ABCCommandArgumentsCaster):
    @staticmethod
    def _literal_eval(token: str) -> Any:
        # simple convert variables like list, dict, int, float
        with suppress(ValueError, SyntaxError):
            token = ast.literal_eval(token)
            return ast.literal_eval(token)
        return token

    @staticmethod
    def _cast_arguments(fn, *args, **kwargs):
        sig = inspect.signature(fn)
        params = sig.parameters
        tc = TypeCaster()
        bound = sig.bind(*args, **kwargs)
        # set defaults, if not set
        bound.apply_defaults()
        for arg_name, values in bound.arguments.items():
            if param := params.get(arg_name):
                # *args
                if isinstance(values, tuple) and param.kind is param.VAR_POSITIONAL:
                    bound.arguments[arg_name] = tuple(tc.cast(param.annotation, v) for v in values)
                # **kwargs
                elif isinstance(values, dict) and param.kind is param.VAR_KEYWORD:
                    bound.arguments[arg_name] = {k: tc.cast(param.annotation, v) for k, v in values.items()}
                # positional
                else:
                    bound.arguments[arg_name] = tc.cast(param.annotation, values)
        return bound.args, bound.kwargs

    def __call__(self, fn: Callable, tokens: list[str]) -> Tuple[Tuple[Any], Dict[str, Any]]:
        sig = inspect.signature(fn)
        param_names = list(sig.parameters.keys())
        args: list[Any] = []
        kwargs = {}

        for token in tokens:
            if "=" in token:
                key, value = token.split("=", 1)
                kwargs[key] = self._literal_eval(value)
            elif len(args) < len(param_names) and param_names[len(args)] not in kwargs:
                args.append(self._literal_eval(token))
            else:
                args.append(self._literal_eval(token))
        # bind parsed arguments, set defaults values
        bound = sig.bind(*args, **kwargs)
        # set defaults, if not set
        bound.apply_defaults()
        return self._cast_arguments(fn, *bound.args, **bound.kwargs)


if __name__ == "__main__":
    cp = CommandParser()
    print(cp("a='12 123' 100"))
