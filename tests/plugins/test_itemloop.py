import pytest

from pypelined.context import ctx_flowdata
from pypelined.plugins.itemloop import ForDict, ForList


@pytest.mark.asyncio
async def test_for_list(init_context_vars):
    params = {
        "lists": [[1, 2], [3, 4]],
        "expression": "item0*item1",
        "filter": "item0*item1>7",
    }
    node = ForList(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == [3, 4, 6]


@pytest.mark.asyncio
async def test_for_dict(init_context_vars):
    params = {
        "lists": [["head1", "head2"], {"name1": "val1", "name2": "val2"}],
        "key": "item0 + ':' + item1_key",
        "val": "item1_val",
    }
    node = ForDict(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == {
        "head1:name1": "val1",
        "head1:name2": "val2",
        "head2:name1": "val1",
        "head2:name2": "val2",
    }
