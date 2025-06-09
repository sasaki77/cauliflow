import asyncio

import pytest

from cauliflow.context import ctx_blackboard
from cauliflow.plugins.buffer import BufferNode
from cauliflow.plugins.message import MessageNode


@pytest.mark.asyncio
async def test_buffer_full(init_context_vars):
    node = BufferNode(
        name="buffer",
        param_dict={
            "size": 5,
            "timeout": 5,
            "input": 1,
        },
    )
    msg = MessageNode(name="msg", param_dict={"msg": "{{ fd.buffer }}", "out_bb": True})
    node.add_child(msg)

    for _ in range(5):
        await node.run()

    blackboard = ctx_blackboard.get()
    assert blackboard["msg"] == [1, 1, 1, 1, 1]


@pytest.mark.asyncio
async def test_buffer_flatten(init_context_vars):
    node = BufferNode(
        name="buffer",
        param_dict={"size": 5, "timeout": 5, "input": [1, 1], "flatten": True},
    )
    msg = MessageNode(name="msg", param_dict={"msg": "{{ fd.buffer }}", "out_bb": True})
    node.add_child(msg)

    for _ in range(3):
        await node.run()

    blackboard = ctx_blackboard.get()
    assert blackboard["msg"] == [1, 1, 1, 1, 1, 1]


@pytest.mark.asyncio
async def test_buffer_timeout(init_context_vars):
    node = BufferNode(
        name="buffer",
        param_dict={
            "size": 5,
            "timeout": 1,
            "input": 1,
        },
    )
    msg = MessageNode(name="msg", param_dict={"msg": "{{ fd.buffer }}", "out_bb": True})
    node.add_child(msg)

    for _ in range(3):
        await node.run()
    await asyncio.sleep(2)

    blackboard = ctx_blackboard.get()
    assert blackboard["msg"] == [1, 1, 1]


@pytest.mark.asyncio
async def test_buffer_not_call_before_timeout(init_context_vars):
    node = BufferNode(
        name="buffer",
        param_dict={
            "size": 5,
            "timeout": 2,
            "input": 1,
        },
    )
    msg = MessageNode(name="msg", param_dict={"msg": "{{ fd.buffer }}", "out_bb": True})
    node.add_child(msg)

    for _ in range(3):
        await node.run()

    blackboard = ctx_blackboard.get()
    assert "msg" not in blackboard
