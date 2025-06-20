import asyncio
from enum import StrEnum
from typing import Any, TypedDict

from aiohttp import ClientResponse, ClientSession, ClientTimeout

from cauliflow.node import ArgSpec, ProcessNode, node


class ResDataFormat(StrEnum):
    JSON = "json"
    TEXT = "text"


class MethodType(StrEnum):
    GET = "get"
    PUT = "put"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class SuccessOut(TypedDict):
    status: int
    data: Any


@node.register("http")
class HTTPNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Send a request to a HTTP endpoint.
      description:
          - Send a request to a HTTP endpoint.
      parameters:
        url:
          description:
            - URL.
        method:
          description:
            - "HTTP method. Following methods are available: get, put, post, patch, and delete."
        timeout:
          description:
            - Timeout in second.
        body:
          description:
            - Request body. This parameter is used for PUT, POST, and PATCH method.
        format:
          description:
            - Data format to decode a response body. It can be either text or json.
    EXAMPLE: |-
      # Get with json format
      # Output: {"http": {"data": {"foo": "bar"}, "status": 200}}
      - http:
          name: "http"
          url: "http://example.com/api/data"
          format: "json"

      # Get with text format
      # Output: {"http": {"data": '{"foo": "bar"}', "status": 200}}
      - http:
          name: "http"
          url: "http://example.com/api/data"
          format: "json"

      # Timeout Error
      # Output: {"http": '{"error": "TimeoutError"}'}
      - http:
          name: "http"
          url: "http://example.com/api/data"
          format: "json"
          timeout: "1"
    """

    async def process(self) -> None:
        timeout = ClientTimeout(total=self.params["timeout"])
        method = self.params["method"]

        try:
            async with ClientSession(timeout=timeout) as session:
                match method:
                    case MethodType.GET:
                        out = await self._get(session)
                    case MethodType.PUT:
                        out = await self._put(session)
                    case MethodType.POST:
                        out = await self._post(session)
                    case MethodType.PATCH:
                        out = await self._patch(session)
                    case MethodType.DELETE:
                        out = await self._delete(session)
                    case _:
                        out = {"error": "Illegal HTTP method"}
                self.output(out)
        except asyncio.TimeoutError:
            out = {"error": "TimeoutError"}
            self.output(out)

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "url": ArgSpec(type="str", required=True),
            "format": ArgSpec(type="str", required=False, default="text"),
            "timeout": ArgSpec(type="float", required=False, default=10),
            "method": ArgSpec(type="str", required=False, default="get"),
            "body": ArgSpec(type="str", required=False, default=""),
        }

    async def _get(self, session: ClientSession) -> SuccessOut:
        async with session.get(self.params["url"]) as resp:
            out = await self._get_output(resp)

        return out

    async def _put(self, session: ClientSession) -> SuccessOut:
        async with session.put(self.params["url"], data=self.params["body"]) as resp:
            out = await self._get_output(resp)

        return out

    async def _post(self, session: ClientSession) -> SuccessOut:
        async with session.post(self.params["url"], data=self.params["body"]) as resp:
            out = await self._get_output(resp)

        return out

    async def _patch(self, session: ClientSession) -> SuccessOut:
        async with session.patch(self.params["url"], data=self.params["body"]) as resp:
            out = await self._get_output(resp)

        return out

    async def _delete(self, session: ClientSession) -> SuccessOut:
        async with session.delete(self.params["url"]) as resp:
            out = await self._get_output(resp)

        return out

    async def _get_output(self, resp: ClientResponse) -> SuccessOut:
        if self.params["format"] == ResDataFormat.JSON:
            data = await resp.json()
        else:
            data = await resp.text()
        out: SuccessOut = {"status": resp.status, "data": data}
        return out
