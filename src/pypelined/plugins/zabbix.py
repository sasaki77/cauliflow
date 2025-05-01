import logging
from functools import singledispatchmethod

from zabbix_utils import AsyncSender, AsyncZabbixAPI, ItemValue

from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable

_logger = logging.getLogger(__name__)


@node.register("zabbix_get_item")
class ZabbixGetItemNode(ProcessNode):
    def __init__(self, name, url, user, password, filter, output):
        super().__init__(name)
        self.url = url
        self.user = user
        self.password = password
        self.filter = filter
        self.output = output

    async def process(self, flowdata: FlowData):
        self.api = AsyncZabbixAPI(url=self.url)
        await self.api.login(user=self.user, password=self.password)

        items = await self.api.item.get(output=self.output, filter=self.filter)

        await self.api.logout()

        flowdata[self.name] = items
        return flowdata


@node.register("zabbix_send")
class ZabbixSend(ProcessNode):
    def __init__(self, name, input, server, port=10051):
        super().__init__(name)
        self.server = server
        self.port = port
        self.input = Variable(input)

    async def process(self, flowdata: FlowData):
        sender = AsyncSender(server=self.server, port=self.port)

        input = self.input.fetch(flowdata)
        items = self._create_items(input)
        response = await sender.send(items)
        _logger.debug(response)

        return flowdata

    @singledispatchmethod
    def _create_items(self, item):
        return [ItemValue(item["hostname"], item["key"], item["value"])]

    @_create_items.register
    def _(self, items: list):
        item_list = []
        for item in items:
            item_list.append(ItemValue(item["hostname"], item["key"], item["value"]))

        return item_list
