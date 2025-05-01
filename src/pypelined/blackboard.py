from collections import UserDict
from contextvars import ContextVar


class BlackBoard(UserDict):
    pass


bb = ContextVar("bb", default=BlackBoard())
