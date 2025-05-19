from collections import UserDict


class FlowData(UserDict):
    def __setitem__(self, key, item):
        if key in self.data:
            raise KeyError(f"Key '{key}' already exists. Overwriting is not allowed.")
        self.data[key] = item
