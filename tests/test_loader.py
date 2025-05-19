from pathlib import Path

import pytest

from cauliflow.context import ctx_blackboard, ctx_flowdata, ctx_macros
from cauliflow.loader import flow_from_yaml


@pytest.mark.asyncio
async def test_sequential(request, init_plugins):
    current_dir = Path(request.fspath).parent
    path = current_dir / "flows/sequential.yml"
    flows = flow_from_yaml(path)
    await flows.run()

    flowdata = ctx_flowdata.get()
    blackboard = ctx_blackboard.get()
    assert blackboard["add1"] == 11
    assert flowdata["add2"] == 12


@pytest.mark.asyncio
async def test_macro(request, init_plugins):
    current_dir = Path(request.fspath).parent
    path = current_dir / "flows/sequential.yml"
    flows = flow_from_yaml(path)

    mcr = ctx_macros.get()
    mcr["init_val"] = 100
    ctx_macros.set(mcr)

    await flows.run()

    flowdata = ctx_flowdata.get()
    blackboard = ctx_blackboard.get()
    assert blackboard["add1"] == 101
    assert flowdata["add2"] == 102


@pytest.mark.asyncio
async def test_concurrent(request, init_plugins):
    current_dir = Path(request.fspath).parent
    path = current_dir / "flows/concurrent.yml"
    flows = flow_from_yaml(path)
    await flows.run()

    blackboard = ctx_blackboard.get()
    assert blackboard["add1"] == 11
    assert blackboard["add2"] == 21


@pytest.mark.asyncio
async def test_composite(request, init_plugins):
    current_dir = Path(request.fspath).parent
    path = current_dir / "flows/composite.yml"
    flows = flow_from_yaml(path)
    await flows.run()

    blackboard = ctx_blackboard.get()
    assert blackboard["add2"] == 12
    assert blackboard["add4"] == 22


@pytest.mark.asyncio
async def test_flowonly(request, init_plugins):
    current_dir = Path(request.fspath).parent
    path = current_dir / "flows/flowonly.yml"
    flows = flow_from_yaml(path)
    await flows.run()

    blackboard = ctx_blackboard.get()
    assert blackboard["add2"] == 12
