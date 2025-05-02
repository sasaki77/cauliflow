from collections import UserDict
from contextvars import ContextVar


class BlackBoard(UserDict):
    pass


blackboard = ContextVar("blackboard", default=BlackBoard())
