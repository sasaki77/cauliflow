import asyncio
import logging

from pypelined.blackboard import BlackBoard
from pypelined.node import Node, node

_logger = logging.getLogger(__name__)


class Flow:
    def __init__(self, root: Node = None):
        self.bb = BlackBoard()
        self.root: Node = node.create("root", _bb=self.bb, name="root")
        self.nodes = {}
        self.nodes["root"] = self.root

    def run(self):
        _logger.debug("run starts")
        asyncio.run(self.root.run())
        _logger.debug("run end")

    def create_node(self, _plugin_name, _parent, name, **kwargs):
        if name in self.nodes:
            _logger.warning(f"{name} is already registerd")
            return

        self.nodes[name] = node.create(_plugin_name, _bb=self.bb, name=name, **kwargs)

        if _parent:
            self.nodes[_parent].add_child(self.nodes[name])
