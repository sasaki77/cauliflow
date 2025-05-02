from collections import UserDict
from contextvars import ContextVar


class Macros(UserDict):
    pass


macros = ContextVar("macros", default=Macros())
