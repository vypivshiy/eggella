class BaseEgellaException(Exception):
    pass


class CommandNotFoundError(BaseEgellaException):
    pass


class CommandParseError(BaseEgellaException):
    pass
