from abc import ABC, abstractmethod

from pypelined.context import (
    ContextNode,
    ctx_blackboard,
    ctx_flowdata,
    ctx_flows,
    ctx_node,
)
from pypelined.logging import get_logger

_logger = get_logger(__name__)


class Node(ABC):
    @abstractmethod
    async def run(self): ...


class TriggerNode(Node):
    def __init__(self, name: str):
        self.name: str = name
        self.child: Node = None

    @abstractmethod
    async def process(self): ...

    async def run(self) -> None:
        ctx_node.set(ContextNode(name=self.name))
        await self.process()
        flows = ctx_flows.get()
        if flows.debug:
            _log_debug()

        await self.child.run()

    def add_child(self, child: Node) -> None:
        self.child = child


class ProcessNode(Node):
    def __init__(self, name: str):
        self.name = name
        self.child: Node = None

    @abstractmethod
    async def process(
        self,
    ): ...

    async def run(self) -> None:
        ctx_node.set(ContextNode(name=self.name))
        await self.process()
        flows = ctx_flows.get()
        if flows.debug:
            _log_debug()
        if self.child is None:
            return
        await self.child.run()

    def add_child(self, child: Node) -> None:
        self.child = child


def _log_debug() -> None:
    flowdata = ctx_flowdata.get()
    blackboard = ctx_blackboard.get()
    _logger.debug(f"flowdata={flowdata}, blackboard={blackboard}")


class NodeFactory:
    registry = {}

    @classmethod
    def create(cls, _name: str, **kwargs) -> Node:
        node_class = cls.registry[_name]
        node = node_class(**kwargs)
        return node

    @classmethod
    def register(cls, name: str):
        _logger.debug(f"{name} is registered")

        def inner_wrapper(wrapped_class: Node):
            if name in cls.registry:
                _logger.warning(f"{name} is already registered.")
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper


node = NodeFactory
