import asyncio
from abc import ABC, abstractmethod

from pypelined.context import (
    ContextFlow,
    ContextNode,
    ctx_blackboard,
    ctx_flow,
    ctx_node,
)
from pypelined.logging import get_logger
from pypelined.node import Node, node

_logger = get_logger(__name__)


class Flow:
    def __init__(self, name=None):
        self.blackboard = ctx_blackboard.get()
        self.name = name
        self.root: Node = node.create("root", name="root")
        self.nodes = {}
        self.nodes["root"] = self.root

    async def run(self):
        ctx_flow.set(ContextFlow(name=self.name))
        _logger.debug("run starts")
        await self.root.run()
        ctx_node.set(ContextNode(name=None))
        _logger.debug("run end")

    def create_node(self, _plugin_name, _parent, name, **kwargs):
        if name in self.nodes:
            _logger.warning(f"{name} is already registerd")
            return

        self.nodes[name] = node.create(_plugin_name, name=name, **kwargs)

        if _parent:
            self.nodes[_parent].add_child(self.nodes[name])


class Flows(ABC):
    @abstractmethod
    async def run(self): ...

    def __init__(self):
        self.flows: list[Flow | Flows] = []

    def append(self, flow):
        self.flows.append(flow)

    def extend(self, flow):
        self.flows.extend(flow)


class ConcurrentFlows(Flows):
    async def run(self):
        async with asyncio.TaskGroup() as tg:
            for task in self.flows:
                tg.create_task(task.run())


class SequentialFlows(Flows):
    async def run(self):
        for task in self.flows:
            await task.run()
