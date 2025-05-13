import pytest

from pypelined.blackboard import BlackBoard
from pypelined.context import ctx_blackboard, ctx_flowdata, ctx_macros
from pypelined.flowdata import FlowData
from pypelined.macros import Macros
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


@pytest.fixture
def init_context_vars():
    bb = BlackBoard()
    fd = FlowData()
    macros = Macros()

    ctx_blackboard.set(bb)
    ctx_flowdata.set(fd)
    ctx_macros.set(macros)


@pytest.fixture(scope="module")
def init_plugins():
    pm = PluginManager()
    pm.init()
