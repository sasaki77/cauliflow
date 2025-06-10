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
        ([1, 2, 3, 4], "item0*2", "item0*2>7", [2, 4, 6]),
        (
            {"key1": 1, "key2": 2},
            "item0_key + '-' + item0_val | str",
            None,
            ["key1-1", "key2-2"],
        ),
        (
            [
                [
                    {"first": "hello, ", "second": "world"},
                    {"first": "foo", "second": "bar"},
                ]
            ],
            "item0.first + item0.second",
            None,
            ["hello, world", "foobar"],
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
@pytest.mark.parametrize(
    "lists, key, val, filter, expected",
    [
        (
            [["head1", "head2"], {"name1": "val1", "name2": "val2"}],
            "item0 + ':' + item1_key",
            "item1_val",
            None,
            {
                "head1:name1": "val1",
                "head1:name2": "val2",
                "head2:name1": "val1",
                "head2:name2": "val2",
            },
        ),
        (
            [1, 2, 3, 4],
            "'key' + item0 |str",
            "item0*2",
            "item0*2>7",
            {"key1": 2, "key2": 4, "key3": 6},
        ),
        (
            {"key1": 1, "key2": 2},
            "item0_key + '-' + item0_val | str",
            "item0_val",
            None,
            {"key1-1": 1, "key2-2": 2},
        ),
    ],
)
async def test_for_dict(init_context_vars, lists, key, val, filter, expected):
    params = {"lists": lists, "key": key, "val": val, "filter": filter}
    node = ForDict(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == expected
