from typing import TypedDict

from cauliflow.logging import get_logger
from cauliflow.node import ArgumentSpec, FlowControlNode, Node, node
from cauliflow.variable import Variable

_logger = get_logger(__name__)


class TypeChild(TypedDict):
    child_if: Node | None
    child_else: Node | None


@node.register("if")
class IfNode(FlowControlNode):
    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        self.cond: Variable | None = None
        self.if_children: TypeChild = {"child_if": None, "child_else": None}

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "condition": {"type": "str", "required": True},
            "child_if": {"type": "node", "required": False, "default": None},
            "child_else": {"type": "node", "required": False, "default": None},
        }

    async def process(self) -> None:
        if self.cond is None:
            self.cond = Variable("{{" + self.params["condition"] + "}}")

        cond = self.cond.fetch()

        if cond and self.if_children["child_if"] is not None:
            await self.if_children["child_if"].run()
        elif self.if_children["child_else"] is not None:
            await self.if_children["child_else"].run()

    def add_child(self, child: Node, param: str | None = None) -> None:
        if param is None:
            self.child = child
            return

        if param not in self.if_children.keys():
            _logger.warning(f"{param} is invalid field")

        self.if_children[param] = child
