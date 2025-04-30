import logging
from abc import ABC, abstractmethod

from pypelined.blackboard import BlackBoard
from pypelined.flowdata import FlowData

_logger = logging.getLogger(__name__)


class NodeFactory:
    registry = {}

    @classmethod
    def create(cls, _name: str, **kwargs):
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


class Node(ABC):
    @abstractmethod
    async def run(self, flowdata: FlowData = {}): ...


class TriggerNode(Node):
    def __init__(self, _bb: BlackBoard, name: str):
        self.name: str = name
        self.child: Node = None
        self.bb = _bb

    @abstractmethod
    async def process(self): ...

    async def run(self, flowdata=None):
        ndata = await self.process(flowdata)
        await self.child.run(ndata)

    def add_child(self, child: Node):
        self.child = child


class ProcessNode(Node):
    def __init__(self, _bb: BlackBoard, name: str):
        self.name = name
        self.child: Node = None
        self.bb = _bb

    @abstractmethod
    async def process(self, flowdata: FlowData): ...

    async def run(self, flowdata={}):
        ndata = await self.process(flowdata)
        if self.child is None:
            return
        await self.child.run(ndata)

    def add_child(self, child: Node):
        self.child = child


node = NodeFactory
