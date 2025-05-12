from abc import ABC, abstractmethod
from typing import NotRequired, TypedDict

from pypelined.context import (
    ContextNode,
    ctx_blackboard,
    ctx_flowdata,
    ctx_flows,
    ctx_node,
)
from pypelined.logging import get_logger
from pypelined.variable import Variable


class ArgumentSpec(TypedDict):
    type: NotRequired[str]
    required: NotRequired[bool]
    default: NotRequired[any]


_logger = get_logger(__name__)


class Node(ABC):
    def __init__(self, name: str, param_dict: dict):
        self.name: str = name
        self.child: Node = None
        self.argument_spec = self.set_argument_spec()
        self.vars = self.make_vars(self.argument_spec, param_dict)
        self.params = {}

    @abstractmethod
    async def process(self): ...

    async def run(self) -> None:
        ctx_node.set(ContextNode(name=self.name))
        self.fetch_params()
        await self.process()
        flows = ctx_flows.get()
        if flows.debug:
            _log_debug()
        if self.child is None:
            return
        await self.child.run()

    def set_argument_spec(self) -> ArgumentSpec:
        return {}

    def make_vars(self, argument_spec, param_dict) -> dict[Variable]:
        vars = {}

        for k, v in argument_spec.items():
            if k in param_dict:
                vars[k] = Variable(param_dict[k])
                continue

            if v.get("required", False):
                msg = f"missing parameter required by {k}"
                raise TypeError(msg)

            if "default" not in v:
                msg = f"default value is not specified required by {k}"
                raise TypeError(msg)

            vars[k] = Variable(v["default"])

        return vars

    def fetch_params(self) -> None:
        for k, v in self.vars.items():
            val = v.fetch()
            self.params[k] = val

    def add_child(self, child: "Node") -> None:
        self.child = child


class TriggerNode(Node):
    pass


class ProcessNode(Node):
    pass


def _log_debug() -> None:
    flowdata = ctx_flowdata.get()
    blackboard = ctx_blackboard.get()
    _logger.debug(f"flowdata={flowdata}, blackboard={blackboard}")


class NodeFactory:
    registry = {}

    @classmethod
    def create(cls, _name: str, name: str, param_dict: dict) -> Node:
        node_class = cls.registry[_name]
        node = node_class(name=name, param_dict=param_dict)
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
