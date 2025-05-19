import pytest
from cauliflow.flowdata import FlowData


def test_flowdata():
    d = FlowData()

    d["a"] = 1
    assert d["a"] == 1

    with pytest.raises(KeyError):
        d["a"] = 1

    d["b"] = 2

    assert d["a"] == 1
    assert d["b"] == 2
