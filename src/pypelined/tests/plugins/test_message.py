import pytest

from pypelined.blackboard import BlackBoard
from pypelined.context import ctx_blackboard, ctx_flowdata, ctx_macros
from pypelined.flowdata import FlowData
from pypelined.macros import Macros
from pypelined.plugins.message import MessageNode


@pytest.fixture
def context_vars():
    bb = BlackBoard()
    fd = FlowData()
    macros = Macros()

    ctx_blackboard.set(bb)
    ctx_flowdata.set(fd)
    ctx_macros.set(macros)


@pytest.mark.asyncio
async def test_message_node():
    node = MessageNode(name="msg", param_dict={"msg": "test"})
    await node.run()
    flowdata = ctx_flowdata.get()
    message = flowdata["msg"]
    assert message == "test"
