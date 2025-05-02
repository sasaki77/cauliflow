from collections import UserDict
from contextvars import ContextVar


class FlowData(UserDict):
    def __setitem__(self, key, item):
        if key in self.data:
            raise KeyError(f"Key '{key}' already exists. Overwriting is not allowed.")
        self.data[key] = item


flowdata = ContextVar("flowdata", default=FlowData())


def init_flowdata():
    flowdata.set(FlowData())
