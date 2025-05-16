from functools import singledispatchmethod

from zabbix_utils import AsyncSender, AsyncZabbixAPI, ItemValue

from pypelined.context import ctx_flowdata
from pypelined.logging import get_logger
from pypelined.node import ArgumentSpec, ProcessNode, node

_logger = get_logger(__name__)


@node.register("zabbix_get_item")
class ZabbixGetItemNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "url": {"type": "str", "required": False, "default": "localhost"},
            "user": {"type": "str", "required": False, "default": "root"},
            "password": {"type": "str", "required": False, "default": "Zabbix"},
            "filter": {"type": "dict", "required": False, "default": None},
            "output": {"type": "list", "required": False, "default": None},
        }

    async def process(self) -> None:
        self.api = AsyncZabbixAPI(url=self.params["url"])
        await self.api.login(user=self.params["user"], password=self.params["password"])

        items = await self.api.item.get(  # type: ignore
            output=self.params["output"], filter=self.params["filter"]
        )

        await self.api.logout()

        fd = ctx_flowdata.get()
        fd[self.name] = items


@node.register("zabbix_send")
class ZabbixSend(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "server": {"type": "str", "required": False, "default": "localhost"},
            "port": {"type": "int", "required": False, "default": 10051},
            "input": {"type": "str", "required": True},
        }

    async def process(self) -> None:
        sender = AsyncSender(server=self.params["server"], port=self.params["port"])

        input = self.params["input"]
        items = self._create_items(input)
        response = await sender.send(items)
        _logger.debug(response)

    @singledispatchmethod
    def _create_items(self, item: dict) -> list[ItemValue]:
        return [ItemValue(item["hostname"], item["key"], item["value"])]

    @_create_items.register
    def _(self, items: list) -> list[ItemValue]:
        item_list = []
        for item in items:
            item_list.append(ItemValue(item["hostname"], item["key"], item["value"]))

        return item_list
