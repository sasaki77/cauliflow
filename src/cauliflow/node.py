from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from cauliflow.context import (
    ContextNode,
    ctx_blackboard,
    ctx_flowdata,
    ctx_flows,
    ctx_node,
)
from cauliflow.logging import get_logger
from cauliflow.variable import Variable


@dataclass(frozen=True)
class ArgSpec:
    type: str
    required: bool = True
    default: Any = None


_logger = get_logger(__name__)

COMMON_ARGUMENT_SPEC: dict[str, ArgSpec] = {
    "out_bb": ArgSpec(type="bool", required=False, default=False),
    "out_field": ArgSpec(type="str", required=False, default=None),
}


class Node(ABC):
    DOCUMENTATION = None
    EXAMPLES = None

    def __init__(self, name: str, param_dict: dict | None = None):
        self.name: str = name
        self.child: Node | None = None
        self.enable_output = False
        self.argument_spec: dict[str, ArgSpec] = {}
        self.argument_spec.update(self.set_argument_spec())
        self.vars = None
        self.params = {}

        if param_dict is not None:
            self.vars = self._make_vars(self.argument_spec, param_dict)

    @abstractmethod
    async def process(self) -> None: ...

    async def run(self) -> None:
        await self._run_self()
        await self._run_child()

    async def _run_self(self) -> None:
        ctx_node.set(ContextNode(name=self.name))
        self._fetch_params()
        await self.process()
        flows = ctx_flows.get()
        if flows.debug:
            _log_debug()

    async def _run_child(self) -> None:
        if self.child is None:
            return
        await self.child.run()

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {}

    def set_common_output_args(self) -> None:
        self.enable_output = True
        self.argument_spec.update(COMMON_ARGUMENT_SPEC)

    def set_params(self, params: dict) -> None:
        self.vars = self._make_vars(self.argument_spec, params)

    def add_child(self, child: "Node", param: str | None = None) -> None:
        self.child = child

    def output(self, value: Any) -> None:
        if self.enable_output is False:
            _logger.warning(
                "output is disabled. call set_common_output_args in set_argumet_spec method"
            )
            return

        param_out_field = self.params["out_field"]
        field = param_out_field if param_out_field else self.name

        ctx = ctx_blackboard if self.params["out_bb"] else ctx_flowdata

        var = ctx.get()
        var[field] = value

    def _make_vars(
        self, argument_spec: dict[str, ArgSpec], param_dict: dict
    ) -> dict[str, Variable]:
        vars = {}

        for k, v in argument_spec.items():
            if k in param_dict:
                vars[k] = Variable(param_dict[k])
                continue

            if v.required is True:
                msg = f"missing parameter required by {k}"
                raise TypeError(msg)

            vars[k] = Variable(v.default)

        return vars

    def _fetch_params(self) -> None:
        if self.vars is None:
            raise TypeError("vars is not initialized")

        for k, v in self.vars.items():
            val = v.fetch()
            self.params[k] = val


class TriggerNode(Node):
    pass


class ProcessNode(Node):
    pass


class FlowControlNode(Node):
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

        def inner_wrapper(wrapped_class: type[Node]):
            if name in cls.registry:
                _logger.warning(f"{name} is already registered.")
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get(cls, name: str) -> Node:
        if name not in cls.registry:
            raise KeyError
        return cls.registry[name]


node = NodeFactory
