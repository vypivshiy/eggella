import ast
import inspect
from contextlib import suppress
from typing import Any, Callable, Dict, List, Tuple

from eggella.command.abc import ABCCommandArgumentsCaster
from eggella.tools.type_caster import TypeCaster

ARGS_AND_KWARGS = Tuple[Tuple[Any], Dict[str, Any]]


class CommandArgumentsCaster(ABCCommandArgumentsCaster):
    @staticmethod
    def _literal_eval(token: str) -> Any:
        # simple convert variables like list, dict, int, float
        with suppress(ValueError, SyntaxError):
            token = ast.literal_eval(token)
            return ast.literal_eval(token)
        return token

    @staticmethod
    def _cast_arguments(fn: Callable, *args: Any, **kwargs: Any):
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

    def __call__(self, fn: Callable, tokens: List[str]) -> ARGS_AND_KWARGS:
        sig = inspect.signature(fn)
        param_names = list(sig.parameters.keys())
        args: List[Any] = []
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
