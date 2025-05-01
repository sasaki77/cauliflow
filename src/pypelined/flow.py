import asyncio
import logging
from abc import ABC, abstractmethod

from pypelined.blackboard import bb
from pypelined.node import Node, node

_logger = logging.getLogger(__name__)


class Flow:
    def __init__(self):
        self.bb = bb.get()
        self.root: Node = node.create("root", _bb=self.bb, name="root")
        self.nodes = {}
        self.nodes["root"] = self.root

    async def run(self):
        _logger.debug("run starts")
        await self.root.run()
        _logger.debug("run end")

    def create_node(self, _plugin_name, _parent, name, **kwargs):
        if name in self.nodes:
            _logger.warning(f"{name} is already registerd")
            return

        self.nodes[name] = node.create(_plugin_name, _bb=self.bb, name=name, **kwargs)

        if _parent:
            self.nodes[_parent].add_child(self.nodes[name])


class Flows(ABC):
    @abstractmethod
    async def run(self): ...


class ConcurrentFlows(Flows):
    def __init__(self):
        self.flows: list[Flow | Flows] = []

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            for task in self.flows:
                tg.create_task(task.run())


class SequentialFlows(Flows):
    def __init__(self):
        self.flows: list[Flow | Flows] = []

    async def run(self):
        for task in self.flows:
            await task.run()
