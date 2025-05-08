from functools import singledispatchmethod

from zabbix_utils import AsyncSender, AsyncZabbixAPI, ItemValue

from pypelined.context import ctx_flowdata
from pypelined.logging import get_logger
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable

_logger = get_logger(__name__)


@node.register("zabbix_get_item")
class ZabbixGetItemNode(ProcessNode):
    def __init__(
        self, name: str, url: str, user: str, password: str, filter: str, output: str
    ):
        super().__init__(name)
        self.url = url
        self.user = user
        self.password = password
        self.filter = filter
        self.output = output

    async def process(self) -> None:
        self.api = AsyncZabbixAPI(url=self.url)
        await self.api.login(user=self.user, password=self.password)

        items = await self.api.item.get(output=self.output, filter=self.filter)

        await self.api.logout()

        fd = ctx_flowdata.get()
        fd[self.name] = items


@node.register("zabbix_send")
class ZabbixSend(ProcessNode):
    def __init__(self, name: str, input: str, server: str, port: int = 10051):
        super().__init__(name)
        self.server = server
        self.port = port
        self.input = Variable(input)

    async def process(self) -> None:
        sender = AsyncSender(server=self.server, port=self.port)

        input = self.input.fetch()
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
