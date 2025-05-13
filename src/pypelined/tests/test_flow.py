import pytest

from pypelined.context import ctx_blackboard, ctx_flowdata
from pypelined.flow import ConcurrentFlows, Flow, SequentialFlows


@pytest.mark.asyncio
async def test_flow(init_plugins):
    flow = Flow("test")

    args1 = {"a": 1, "b": 1}
    args2 = {"a": "{{ fd['add1'] }}", "b": 1}
    args3 = {"a": "{{ fd['add2'] }}", "b": 1}

    flow.create_node("test.addnode", "root", "add1", args1)
    flow.create_node("test.addnode", "add1", "add2", args2)
    flow.create_node("test.addnode", "add2", "add3", args3)

    await flow.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["add1"] == 2
    assert flowdata["add2"] == 3
    assert flowdata["add3"] == 4


@pytest.mark.asyncio
async def test_sequential_flows(init_plugins):
    flow1 = Flow("test")
    args1 = {"a": 1, "b": 1, "out_bb": True}
    flow1.create_node("test.addnode", "root", "add1", args1)

    flow2 = Flow("test")
    args2 = {"a": "{{ bb['add1']}}", "b": 1}
    flow2.create_node("test.addnode", "root", "add2", args2)

    flows = SequentialFlows()
    flows.append(flow1)
    flows.append(flow2)

    await flows.run()
    flowdata = ctx_flowdata.get()
    blackboard = ctx_blackboard.get()
    assert blackboard["add1"] == 2
    assert flowdata["add2"] == 3


@pytest.mark.asyncio
async def test_concurrent_flows(init_plugins):
    flow1 = Flow("test")
    args1 = {"a": 1, "b": 1, "out_bb": True}
    flow1.create_node("test.addnode", "root", "add1", args1)

    flow2 = Flow("test")
    args2 = {"a": 1, "b": 1, "out_bb": True}
    flow2.create_node("test.addnode", "root", "add2", args2)

    flows = ConcurrentFlows()
    flows.append(flow1)
    flows.append(flow2)

    await flows.run()
    blackboard = ctx_blackboard.get()
    assert blackboard["add1"] == 2
    assert blackboard["add2"] == 2
