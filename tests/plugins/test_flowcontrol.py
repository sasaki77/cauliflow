import pytest
from cauliflow.context import ctx_flowdata
from cauliflow.flow import Flow


@pytest.mark.asyncio
async def test_if_child_if(init_plugins):
    flow = Flow("test")

    args1 = {"a": 1, "b": 1}
    args2 = {"condition": "fd['add1']  == 2"}
    args3 = {"a": "{{ fd['add1'] }}", "b": 1}
    args4 = {"a": "{{ fd['add1'] }}", "b": 2}
    args5 = {"a": 1, "b": 1}

    flow.create_node("test.addnode", "root", "add1", args1)
    flow.create_node("if", "add1", "if", args2)
    flow.create_node("test.addnode", "if.child_if", "add3", args3)
    flow.create_node("test.addnode", "if.child_else", "add4", args4)
    flow.create_node("test.addnode", "if", "add5", args5)

    await flow.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["add1"] == 2
    assert flowdata["add3"] == 3
    assert "add4" not in flowdata
    assert flowdata["add5"] == 2


@pytest.mark.asyncio
async def test_if_child_else(init_plugins):
    flow = Flow("test")

    args1 = {"a": 1, "b": 1}
    args2 = {"condition": "fd['add1']  != 2"}
    args3 = {"a": "{{ fd['add1'] }}", "b": 1}
    args4 = {"a": "{{ fd['add1'] }}", "b": 2}
    args5 = {"a": 1, "b": 1}

    flow.create_node("test.addnode", "root", "add1", args1)
    flow.create_node("if", "add1", "if", args2)
    flow.create_node("test.addnode", "if.child_if", "add3", args3)
    flow.create_node("test.addnode", "if.child_else", "add4", args4)
    flow.create_node("test.addnode", "if", "add5", args5)

    await flow.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["add1"] == 2
    assert "add3" not in flowdata
    assert flowdata["add4"] == 4
    assert flowdata["add5"] == 2
