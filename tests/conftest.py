import pytest

from cauliflow.blackboard import BlackBoard
from cauliflow.context import ctx_blackboard, ctx_flowdata, ctx_macros
from cauliflow.flowdata import FlowData
from cauliflow.macros import Macros
from cauliflow.node import ArgSpec, Node, node
from cauliflow.plugin_manager import PluginManager


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

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "a": ArgSpec(type="int", required=True),
            "b": ArgSpec(type="int", required=True),
            "out_bb": ArgSpec(type="bool", required=False, default=False),
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
