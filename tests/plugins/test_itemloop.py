import pytest

from cauliflow.context import ctx_flowdata
from cauliflow.plugins.itemloop import ForDict, ForList


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expression, filter, expected",
    [
        ([[1, 2], [3, 4]], "item0*item1", "item0*item1>7", [3, 4, 6]),
        (
            [["head1", "head2"], {"name1": "val1", "name2": "val2"}],
            "item0+':'+item1_val",
            None,
            ["head1:val1", "head1:val2", "head2:val1", "head2:val2"],
        ),
    ],
)
async def test_for_list(init_context_vars, lists, expression, filter, expected):
    params = {"lists": lists, "expression": expression, "filter": filter}
    node = ForList(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == expected


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
