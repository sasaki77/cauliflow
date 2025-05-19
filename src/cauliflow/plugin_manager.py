import importlib
import pkgutil

import cauliflow.plugins as plugins


# https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
def _iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


class PluginManager:
    def __init__(self):
        pass

    def init(self):
        self._load_buildin()

    def _load_buildin(self):
        for finder, name, ispkg in _iter_namespace(plugins):
            importlib.import_module(name)
