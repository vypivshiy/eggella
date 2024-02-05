class BaseEgellaException(Exception):
    pass


class CommandNotFoundError(BaseEgellaException):
    pass


class CommandParseError(BaseEgellaException):
    pass


class CommandTooManyArgumentsError(BaseEgellaException):
    pass


class CommandArgumentValueError(BaseEgellaException):
    pass


class CommandRuntimeError(BaseEgellaException):
    pass
