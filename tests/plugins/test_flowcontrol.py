import pytest

from cauliflow.context import ctx_blackboard, ctx_flowdata
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    [
        ("sequential"),
        ("concurrent"),
    ],
)
async def test_foreach(init_plugins, mode):
    flow = Flow("test")

    args_for = {"items": [1, 2, 3], "item_name": "foo", "mode": mode}
    args_msg = {
        "msg": "{{ fd.foo }}",
        "out_bb": True,
        "out_field": "{{ 'field' + fd.foo | str }}",
    }

    flow.create_node("foreach", "root", "for", args_for)
    flow.create_node("message", "for.child_for", "msg", args_msg)

    await flow.run()

    bb = ctx_blackboard.get()
    assert bb == {"field1": 1, "field2": 2, "field3": 3}
    fd = ctx_flowdata.get()
    assert fd == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, mode",
    [
        ([1, 2, 3], "invalid_mode"),
        (1, "concurrent"),
    ],
)
async def test_foreach_valueerror(init_plugins, items, mode):
    flow = Flow("test")

    args_for = {"items": items, "item_name": "foo", "mode": mode}
    args_msg = {
        "msg": "{{ fd.foo }}",
        "out_bb": True,
        "out_field": "{{ 'field' + fd.foo | str }}",
    }

    flow.create_node("foreach", "root", "for", args_for)
    flow.create_node("message", "for.child_for", "msg", args_msg)

    with pytest.raises(ValueError):
        await flow.run()


@pytest.mark.asyncio
async def test_dispatch_sequential(init_plugins):
    flow = Flow("test")

    args_msg = {"msg": 10}
    args_dispatch = {"mode": "sequential"}
    args1 = {"a": "{{ fd.msg }}", "b": 1}
    args2 = {"a": "{{ fd.msg }}", "b": "{{ fd.add1 }}"}
    args3 = {"a": "{{ fd.msg }}", "b": "{{ fd.add2 }}"}

    flow.create_node("message", "root", "msg", args_msg)
    flow.create_node("dispatch", "msg", "dispatch", args_dispatch)
    flow.create_node("test.addnode", "dispatch.targets", "add1", args1)
    flow.create_node("test.addnode", "dispatch.targets", "add2", args2)
    flow.create_node("test.addnode", "dispatch.targets", "add3", args3)

    await flow.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["add1"] == 11
    assert flowdata["add2"] == 21
    assert flowdata["add3"] == 31


@pytest.mark.asyncio
async def test_dispatch_concurrent(init_plugins):
    flow = Flow("test")

    args_msg = {"msg": 10}
    args_dispatch = {"mode": "concurrent"}
    args1 = {"a": "{{ fd.msg }}", "b": 1}
    args2 = {"a": "{{ fd.msg }}", "b": 2}
    args3 = {"a": "{{ fd.msg }}", "b": 3}

    flow.create_node("message", "root", "msg", args_msg)
    flow.create_node("dispatch", "msg", "dispatch", args_dispatch)
    flow.create_node("test.addnode", "dispatch.targets", "add1", args1)
    flow.create_node("test.addnode", "dispatch.targets", "add2", args2)
    flow.create_node("test.addnode", "dispatch.targets", "add3", args3)

    await flow.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["add1"] == 11
    assert flowdata["add2"] == 12
    assert flowdata["add3"] == 13
