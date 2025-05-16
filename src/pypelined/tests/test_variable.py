import pytest

from pypelined.blackboard import BlackBoard
from pypelined.context import ctx_blackboard, ctx_flowdata, ctx_macros
from pypelined.flowdata import FlowData
from pypelined.macros import Macros
from pypelined.variable import Variable


@pytest.fixture
def context_vars():
    bb = BlackBoard({"bb1": "foo"})
    fd = FlowData({"fd1": "bar"})
    macros = Macros({"mc1": "foobar"})

    ctx_blackboard.set(bb)
    ctx_flowdata.set(fd)
    ctx_macros.set(macros)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("", ""),
        ("''", "''"),
        ("{{ -1 }}", -1),
        ("This is a test.", "This is a test."),
        ("{{ [1, 2, 3] }}", [1, 2, 3]),
        ("{{ {'key': 'val'} }}", {"key": "val"}),
        ("{{ 'foo' + 'bar' }}", "foobar"),
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
        ("{{ 'bb1' in bb }}", True),
        ("{{ 'bb1' not in bb }}", False),
        ("{{ bb['bb1'] + fd['fd1'] + '-' + macro['mc1'] }}", "foobar-foobar"),
        ("{{ bb['bb1'] }}bar-{{ macro['mc1'] }}", "foobar-foobar"),
        ("{{ bb['bb1'] }} bar-  {{ macro['mc1'] }}", "foobar-  foobar"),
        ("{{ bb['bb1'] + ' ' }} bar-  {{ macro['mc1'] }}", "foo bar-  foobar"),
    ],
)
def test_variable(context_vars, input, expected):
    var = Variable(input)
    data = var.fetch()
    assert data == expected
