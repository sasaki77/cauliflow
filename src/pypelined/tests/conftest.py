import pytest

from pypelined.context import ctx_blackboard, ctx_flowdata
from pypelined.node import ArgumentSpec, Node, node
from pypelined.plugin_manager import PluginManager


@node.register("test.addnode")
class AddNode(Node):
    async def process(self) -> None:
        outbb = self.params["out_bb"]
        _sum = self.params["a"] + self.params["b"]
        if outbb:
            bb = ctx_blackboard.get()
            bb[self.name] = _sum
        else:
            flowdata = ctx_flowdata.get()
            flowdata[self.name] = _sum

    def set_argument_spec(self) -> ArgumentSpec:
        return {
            "a": {"type": "int", "required": True},
            "b": {"type": "int", "required": True},
            "out_bb": {"type": "bool", "required": False, "default": False},
        }


@pytest.fixture(scope="module")
def init_plugins():
    pm = PluginManager()
    pm.init()
