import pytest
from cauliflow.context import ctx_flowdata
from cauliflow.plugins.message import MessageNode


@pytest.mark.asyncio
async def test_message_node(init_context_vars):
    node = MessageNode(name="node", param_dict={"msg": "test"})
    await node.run()
    flowdata = ctx_flowdata.get()
    message = flowdata["node"]
    assert message == "test"
