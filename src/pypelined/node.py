import logging
from abc import ABC, abstractmethod

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
    async def run(self): ...


class TriggerNode(Node):
    def __init__(self, name: str):
        self.name: str = name
        self.child: Node = None

    @abstractmethod
    async def process(self): ...

    async def run(self):
        await self.process()
        await self.child.run()

    def add_child(self, child: Node):
        self.child = child


class ProcessNode(Node):
    def __init__(self, name: str):
        self.name = name
        self.child: Node = None

    @abstractmethod
    async def process(
        self,
    ): ...

    async def run(
        self,
    ):
        await self.process()
        if self.child is None:
            return
        await self.child.run()

    def add_child(self, child: Node):
        self.child = child


node = NodeFactory
