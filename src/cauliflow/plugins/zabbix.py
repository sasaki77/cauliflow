from functools import singledispatchmethod

from zabbix_utils import AsyncSender, AsyncZabbixAPI, ItemValue

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node

_logger = get_logger(__name__)


@node.register("zabbix_get_item")
class ZabbixGetItemNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "url": ArgSpec(type="str", required=False, default="localhost"),
            "user": ArgSpec(type="str", required=False, default="root"),
            "password": ArgSpec(type="str", required=False, default="Zabbix"),
            "filter": ArgSpec(type="dict", required=False, default=None),
            "output": ArgSpec(type="list", required=False, default=None),
        }

    async def process(self) -> None:
        self.api = AsyncZabbixAPI(url=self.params["url"])
        await self.api.login(user=self.params["user"], password=self.params["password"])

        items = await self.api.item.get(  # type: ignore
            output=self.params["output"], filter=self.params["filter"]
        )

        await self.api.logout()
        self.output(items)


@node.register("zabbix_send")
class ZabbixSend(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "server": ArgSpec(type="str", required=False, default="localhost"),
            "port": ArgSpec(type="int", required=False, default=10051),
            "input": ArgSpec(type="str", required=True),
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
