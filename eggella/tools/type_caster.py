import inspect
import sys
from typing import Any, Type, Union, get_args, get_origin

NoneType = type(None)


class TypeCaster:
    @classmethod
    def _typing_to_builtin(cls, type_hint: Type) -> Type:
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is not None and args:
            # Recursively convert the nested generic types
            converted_args = tuple(cls._typing_to_builtin(arg) for arg in args)
            return origin[converted_args]
        else:
            return type_hint

    @classmethod
    def cast(cls, type_hint: Type, value: Any) -> Any:
        # extracted annotation from `inspect.get_annotations`
        if type_hint is inspect.Parameter.empty:
            return str(value)

        if sys.version_info >= (3, 9):
            type_hint = cls._typing_to_builtin(type_hint)
        origin = get_origin(type_hint)
        args = get_args(type_hint)
        # None
        if value is None and type_hint is not bool:
            return value

        if origin is not None and args:
            # list
            if origin is list:
                return [cls.cast(type_hint=args[0], value=v) for v in value]
            # dict
            elif origin is dict:
                key_type, value_type = args
                return {
                    cls.cast(type_hint=key_type, value=k): cls.cast(type_hint=value_type, value=v)
                    for k, v in value.items()
                }
            # Optional
            elif origin is Union:
                if value is None and NoneType in args:
                    return None
                # in python3.8 raise TypeError: issubclass() arg 1 must be a class
                # example _cast_type(Optional[List[int]], [])
                non_none_args = [arg for arg in args if arg is not NoneType]
                if len(non_none_args) == 1:
                    return cls.cast(type_hint=non_none_args[0], value=value)
        # bool cast
        elif type_hint is bool:
            return bool(value)
        else:
            # direct cast
            return type_hint(value)
