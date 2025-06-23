import asyncio
import json

import pytest
from aioresponses import CallbackResult, aioresponses

from cauliflow.context import ctx_flowdata
from cauliflow.plugins.http import HTTPNode


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "format, expected",
    [
        ("json", {"foo": "bar"}),
        ("text", '{"foo": "bar"}'),
    ],
)
async def test_get_data(init_context_vars, mock_aioresponse, format, expected):
    url = "http://example.com/api/data"
    expected_data = {"foo": "bar"}
    mock_aioresponse.get(url, payload=expected_data)

    node = HTTPNode(name="node", param_dict={"url": url, "format": format})
    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["status"] == 200
    assert data["data"] == expected


@pytest.mark.asyncio
async def test_get_data_timeout(init_context_vars, mock_aioresponse):
    url = "http://example.com/api/data"
    mock_aioresponse.get(url, exception=asyncio.TimeoutError())

    node = HTTPNode(name="node", param_dict={"url": url, "format": format})
    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["error"] == "TimeoutError"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "format, expected",
    [
        ("json", {"foo": "bar"}),
        ("text", '{"foo": "bar"}'),
    ],
)
async def test_put_data(init_context_vars, mock_aioresponse, format, expected):
    url = "http://example.com/api/data"
    expected_data = {"foo": "bar"}

    def request_callback(url, **kwargs):
        captured_body = kwargs.get("data", {})
        assert captured_body == "test"
        return CallbackResult(status=201, body=json.dumps(expected_data))

    mock_aioresponse.put(url, callback=request_callback)

    node = HTTPNode(
        name="node",
        param_dict={"url": url, "format": format, "method": "put", "body": "test"},
    )

    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["status"] == 201
    assert data["data"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "format, expected",
    [
        ("json", {"foo": "bar"}),
        ("text", '{"foo": "bar"}'),
    ],
)
async def test_post_data(init_context_vars, mock_aioresponse, format, expected):
    url = "http://example.com/api/data"
    expected_data = {"foo": "bar"}

    def request_callback(url, **kwargs):
        captured_body = kwargs.get("data", {})
        assert captured_body == "test"
        return CallbackResult(status=201, body=json.dumps(expected_data))

    mock_aioresponse.post(url, callback=request_callback)

    node = HTTPNode(
        name="node",
        param_dict={"url": url, "format": format, "method": "post", "body": "test"},
    )

    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["status"] == 201
    assert data["data"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "format, expected",
    [
        ("json", {"foo": "bar"}),
        ("text", '{"foo": "bar"}'),
    ],
)
async def test_patch_data(init_context_vars, mock_aioresponse, format, expected):
    url = "http://example.com/api/data"
    expected_data = {"foo": "bar"}

    def request_callback(url, **kwargs):
        captured_body = kwargs.get("data", {})
        assert captured_body == "test"
        return CallbackResult(status=201, body=json.dumps(expected_data))

    mock_aioresponse.patch(url, callback=request_callback)

    node = HTTPNode(
        name="node",
        param_dict={"url": url, "format": format, "method": "patch", "body": "test"},
    )

    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["status"] == 201
    assert data["data"] == expected


@pytest.mark.asyncio
async def test_delete_data(init_context_vars, mock_aioresponse):
    url = "http://example.com/api/data"
    mock_aioresponse.delete(url, status=204)

    node = HTTPNode(name="node", param_dict={"url": url, "method": "delete"})
    await node.run()
    flowdata = ctx_flowdata.get()
    data = flowdata["node"]
    assert data["status"] == 204
