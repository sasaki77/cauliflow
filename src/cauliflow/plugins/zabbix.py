from functools import singledispatchmethod

from zabbix_utils import AsyncSender, AsyncZabbixAPI, ItemValue

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node

_logger = get_logger(__name__)


@node.register("zabbix_get_item")
class ZabbixGetItemNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Get Zabbix item with Zabbix API
      description:
        - Get Zabbix item with Zabbix API
      parameters:
        url:
          description:
            - URL for Zabbix server
        user:
          description:
            - User name for Zabbix API.
        password:
          description:
            - Password for Zabbix API.
        filter:
          description:
            - Filter to get the result mathed.
        output:
          description:
            - Properties to be returned.
    EXAMPLE: |-
      # Get Zabbix items only matched Template EPICS
      # Output: [{'key_': 'item.key1',  'name': 'foo, 'itemid': 1}]
      - zabbix_get_item:
          name: "zabbix_get"
          url: "http:/localhost"
          user: "Admin"
          password: "Zabbix"
          output: ["itemid", "name", "key_"]
          filter: { "key_": null, "host": "Template EPICS" }
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "url": ArgSpec(type="str", required=False, default="localhost"),
            "user": ArgSpec(type="str", required=False, default="root"),
            "password": ArgSpec(type="str", required=False, default="Zabbix"),
            "filter": ArgSpec(type="dict", required=False, default=None),
            "output": ArgSpec(type="list[str]", required=False, default=None),
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
    """
    DOCUMENTATION:
      short_description: Send item values to a Zabbix server.
      description:
        - Send item values to a Zabbix server via Zabbix sender protocol.
      parameters:
        server:
          description:
            - Zabbix server address.
        port:
          description:
            - Zabbix server port.
        items:
          description:
            - List of items or dict of item to send.
            - "Item must have following keys: hostname, key, and value."
    EXAMPLE: |-
      # Send two items to Zabbix server.
      # Output: No output
      - zabbix_send:
          name: "zabbix_send"
          server: "localhost"
          port: 10051
          items:
            - {"hostname": "foo", "key": "bar", "val": 1}
            - {"hostname": "foo", "key": "foobar", "val": 1}

      # Send items from flowdata to Zabbix server.
      # Output: No output
      - zabbix_send:
          name: "zabbix_send"
          items: "{{ fd.zabbix_item }}"
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "server": ArgSpec(type="str", required=False, default="localhost"),
            "port": ArgSpec(type="int", required=False, default=10051),
            "items": ArgSpec(type="dict|list[dict]", required=True),
        }

    async def process(self) -> None:
        sender = AsyncSender(server=self.params["server"], port=self.params["port"])

        input = self.params["items"]
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
