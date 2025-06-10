import pytest

from cauliflow.blackboard import BlackBoard
from cauliflow.context import ctx_blackboard, ctx_flowdata, ctx_macros
from cauliflow.flowdata import FlowData
from cauliflow.macros import Macros
from cauliflow.variable import Variable


@pytest.fixture
def context_vars():
    bb = BlackBoard({"bb1": "foo", "dict": {"foo": "bar"}})
    fd = FlowData({"fd1": "bar"})
    macros = Macros({"mc1": "foobar"})

    ctx_blackboard.set(bb)
    ctx_flowdata.set(fd)
    ctx_macros.set(macros)


@pytest.mark.parametrize(
    "input,expected",
    [
        # Basic expression
        ("", ""),
        ("''", "''"),
        ("{{ -1 }}", -1),
        ("This is a test.", "This is a test."),
        ("{{ [1, 2, 3] }}", [1, 2, 3]),
        ("{{ {'key': 'val'} }}", {"key": "val"}),
        ("{{ 'foo' + 'bar' }}", "foobar"),
        ("{{ 'foo\t' + 'bar' }}", "foo\tbar"),
        ("{{ 'foo\n' + 'bar' }}", "foo\nbar"),
        ("{{ True or False }}", True),
        ("{{ True and False }}", False),
        ("{{ not True }}", False),
        ("{{ 1 > 0 }}", True),
        ("{{ 1 < 0 }}", False),
        ("{{ 1 == 1 }}", True),
        ("{{ 1 != 1 }}", False),
        ("{{ 1 >= 1 }}", True),
        ("{{ 1 <= 1 }}", True),
        ("{{ None is None }}", True),
        ("{{ None is not None }}", False),
        ("{{ (1+1)*(2-1)/2 }}", 1),
        ("{{ 0.1 + 0.1 }}", 0.2),
        ("{{ 5//3 }}", 1),
        ("{{ 5%3 }}", 2),
        # Filters
        ("{{ 'test' + 1 | str }}", "test1"),
        ("{{ '1' | float }}", 1),
        ("{{ '1' | float | int | str }}", "1"),
        ("{{ {'key1': 1, 'key2': 2} | dict_keys() }}", ["key1", "key2"]),
        ("{{ {'key1': 1, 'key2': 2} | dict_values }}", [1, 2]),
        (
            "{{ {'key1': 1, 'key2': 2} | dict2item('k','v') }}",
            [{"k": "key1", "v": 1}, {"k": "key2", "v": 2}],
        ),
        # Variable
        ("{{ 'bb1' in bb }}", True),
        ("{{ 'bb1' not in bb }}", False),
        ("{{ bb['bb1'] + fd['fd1'] + '-' + macro['mc1'] }}", "foobar-foobar"),
        ("{{ bb.bb1 + fd.fd1 + '-' + macro.mc1 }}", "foobar-foobar"),
        ("{{ bb['bb1'] }}bar-{{ macro['mc1'] }}", "foobar-foobar"),
        ("{{ bb['bb1'] }} bar-  {{ macro['mc1'] }}", "foobar-  foobar"),
        ("{{ bb['bb1'] + ' ' }} bar-  {{ macro['mc1'] }}", "foo bar-  foobar"),
        ("{{ bb['dict'] | dict_keys }}", ["foo"]),
        ("{{ bb.dict.foo }}", "bar"),
        ("{{ bb.dict['foo'] }}", "bar"),
    ],
)
def test_variable(context_vars, input, expected):
    var = Variable(input)
    data = var.fetch()
    assert data == expected
