import asyncio
from abc import ABC, abstractmethod

from cauliflow.context import (
    ContextFlow,
    ContextNode,
    ctx_blackboard,
    ctx_flow,
    ctx_node,
)
from cauliflow.logging import get_logger
from cauliflow.node import Node, node

_logger = get_logger(__name__)


class Flow:
    def __init__(self, name: str | None = None):
        self.blackboard = ctx_blackboard.get()
        self.name = name
        self.root: Node = node.create("root", name="root", param_dict={})
        self.nodes: dict[str, Node] = {}
        self.nodes["root"] = self.root

    async def run(self) -> None:
        ctx_flow.set(ContextFlow(name=self.name))
        _logger.debug("run starts")
        await self.root.run()
        ctx_node.set(ContextNode(name=None))
        _logger.debug("run end")

    def create_node(
        self, _plugin_name: str, _parent: str, name: str, param_dict: dict
    ) -> None:
        if name in self.nodes:
            _logger.warning(f"{name} is already registerd")
            return

        self.nodes[name] = node.create(_plugin_name, name=name, param_dict=param_dict)

        if not _parent:
            return

        if "." not in _parent:
            self.nodes[_parent].add_child(self.nodes[name])
            return

        parent, field = _parent.split(".")
        self.nodes[parent].add_child(self.nodes[name], field)


class Flows(ABC):
    @abstractmethod
    async def run(self): ...

    def __init__(self):
        self.flows: list[Flow | Flows] = []

    def append(self, flow: "Flow | Flows"):
        self.flows.append(flow)

    def extend(self, flow: list["Flow | Flows"]):
        self.flows.extend(flow)


class ConcurrentFlows(Flows):
    async def run(self) -> None:
        async with asyncio.TaskGroup() as tg:
            for task in self.flows:
                tg.create_task(task.run())


class SequentialFlows(Flows):
    async def run(self) -> None:
        for task in self.flows:
            await task.run()
