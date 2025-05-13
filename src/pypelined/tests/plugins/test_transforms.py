import pytest

from pypelined.context import ctx_flowdata
from pypelined.plugins.transforms import (
    ConcatNode,
    DictKeysNode,
    DictValuesNode,
    MutateNode,
)


@pytest.mark.asyncio
async def test_dictkeys(init_context_vars):
    params = {
        "input": {"key1": "val1", "key2": "val2"},
    }
    node = DictKeysNode(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == ["key1", "key2"]


@pytest.mark.asyncio
async def test_dictvalues(init_context_vars):
    params = {
        "input": {"key1": "val1", "key2": "val2"},
    }
    node = DictValuesNode(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == ["val1", "val2"]


@pytest.mark.asyncio
async def test_mutate(init_context_vars):
    params = {
        "target": [{"origin": "head.pvname1"}, {"origin": "head.pvname2"}],
        "copy": {"origin": "copy"},
        "split": {"copy": "."},
    }
    node = MutateNode(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == [
        {"origin": "head.pvname1", "copy": ["head", "pvname1"]},
        {"origin": "head.pvname2", "copy": ["head", "pvname2"]},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, expected",
    [
        (
            {"first": ["head1:", "head2:"], "second": ["pv1", "pv2"]},
            ["head1:pv1", "head2:pv2"],
        ),
        (
            {"first": "head1:", "second": ["pv1", "pv2"]},
            ["head1:pv1", "head1:pv2"],
        ),
        (
            {"first": ["head1:", "head2:"], "second": "pv1"},
            ["head1:pv1", "head2:pv1"],
        ),
        (
            {"first": "head1:", "second": "pv1"},
            "head1:pv1",
        ),
    ],
)
async def test_concat(init_context_vars, params, expected):
    node = ConcatNode(name="node", param_dict=params)
    await node.run()
    flowdata = ctx_flowdata.get()
    assert flowdata["node"] == expected
