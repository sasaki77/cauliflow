import asyncio
import subprocess
import sys
from pathlib import Path

import pytest
from aioca import caget, caput, purge_channel_caches

from cauliflow.context import ctx_blackboard, ctx_flowdata
from cauliflow.plugins.ca import CagetNode, CamonitorNode, CaputNode
from cauliflow.plugins.message import MessageNode

SOFT_RECORDS = str(Path(__file__).parent / "ca_records.db")
PREFIX = "ET_SASAKI"


@pytest.fixture
def ioc():
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "epicscorelibs.ioc",
            "-m",
            f"head={PREFIX}",
            "-d",
            SOFT_RECORDS,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    yield process
    purge_channel_caches()
    try:
        process.communicate("exit")
    except ValueError:
        pass


@pytest.mark.asyncio
async def test_camonitor(ioc, init_context_vars):
    blackboard = ctx_blackboard.get()
    blackboard["msg"] = []

    pvname = f"{PREFIX}:LONGOUT"
    node = CamonitorNode(name="ca", param_dict={"pvname": pvname})
    msg = MessageNode(
        name="msg", param_dict={"msg": "{{ bb.msg + [fd.ca] }}", "out_bb": True}
    )
    node.add_child(msg)

    async def caput_test():
        await asyncio.sleep(2.0)
        await caput(pvname, 5.0)
        await asyncio.sleep(0.1)
        await caput(pvname, 6.0)

    try:
        async with asyncio.timeout(5):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(node.run())
                tg.create_task(caput_test())
    except TimeoutError:
        pass

    assert len(blackboard["msg"]) == 3
    assert blackboard["msg"][1]["value"] == 5.0
    assert blackboard["msg"][2]["value"] == 6.0


@pytest.mark.asyncio
async def test_caget_ok(ioc, init_context_vars):
    pvname = f"{PREFIX}:LONGOUT"
    node = CagetNode(name="node", param_dict={"pvname": pvname})

    await caput(pvname, 1)
    await node.run()

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert data["name"] == pvname
    assert data["value"] == 1.0
    assert data["status"] == 0
    assert data["severity"] == 0
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_caget_ok_list(ioc, init_context_vars):
    pvlist = [f"{PREFIX}:LONGOUT", f"{PREFIX}:AO"]
    node = CagetNode(name="node", param_dict={"pvname": pvlist})

    await caput(pvlist[0], 2)
    await caput(pvlist[1], 2)
    await node.run()

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert len(data) == 2
    for d, pv in zip(data, pvlist):
        assert d["name"] == pv
        assert d["value"] == 2.0
        assert d["status"] == 0
        assert d["severity"] == 0
        assert d["ok"] is True


@pytest.mark.asyncio
async def test_caget_ng(ioc, init_context_vars):
    pvname = "JOHN_DOE"
    node = CagetNode(name="node", param_dict={"pvname": pvname, "timeout": 0.1})

    await node.run()

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert data["name"] == pvname
    assert data["ok"] is False


@pytest.mark.asyncio
async def test_caput_ok(ioc, init_context_vars):
    pvname = f"{PREFIX}:LONGOUT"
    val = 10
    node = CaputNode(name="node", param_dict={"pvname": pvname, "value": val})

    await node.run()

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert data["name"] == pvname
    assert data["ok"] is True

    get_val = await caget(pvname)

    assert get_val == val


@pytest.mark.asyncio
async def test_caput_list(ioc, init_context_vars):
    pvlist = [f"{PREFIX}:LONGOUT", f"{PREFIX}:AO"]
    values = [1, 2]
    node = CaputNode(name="node", param_dict={"pvname": pvlist, "value": values})

    await node.run()

    get_vals = await caget(pvlist)

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert len(data) == 2
    for d, pv, name, v in zip(data, get_vals, pvlist, values):
        assert d["name"] == name
        assert d["ok"] is True
        assert pv == v


@pytest.mark.asyncio
async def test_caput_list_with_repeat(ioc, init_context_vars):
    pvlist = [f"{PREFIX}:LONGOUT", f"{PREFIX}:AO"]
    value = 10
    node = CaputNode(
        name="node",
        param_dict={"pvname": pvlist, "value": value, "repeat_value": True},
    )

    await node.run()

    get_vals = await caget(pvlist)

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert len(data) == 2
    for d, pv, name in zip(data, get_vals, pvlist):
        assert d["name"] == name
        assert d["ok"] is True
        assert pv == value


@pytest.mark.asyncio
async def test_caput_ng(ioc, init_context_vars):
    pvname = "JOHN_DOE"
    val = 10
    node = CaputNode(
        name="node", param_dict={"pvname": pvname, "value": val, "timeout": 1}
    )

    await node.run()

    flowdata = ctx_flowdata.get()
    data = flowdata["node"]

    assert data["name"] == pvname
    assert data["ok"] is False
