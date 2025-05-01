from collections import UserDict
from contextvars import ContextVar


class FlowData(UserDict):
    def __setitem__(self, key, item):
        if key in self.data:
            raise KeyError(f"Key '{key}' already exists. Overwriting is not allowed.")
        self.data[key] = item


fd = ContextVar("fd", default=FlowData())


def init_flowdata():
    fd.set(FlowData())
