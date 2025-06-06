from typing import TypedDict

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, FlowControlNode, Node, node
from cauliflow.variable import Variable

_logger = get_logger(__name__)


class TypeChild(TypedDict):
    child_if: Node | None
    child_else: Node | None


@node.register("if")
class IfNode(FlowControlNode):
    """
    DOCUMENTATION:
      short_description: Control flow with if-then-else construction.
      description:
        - Control flow with if-then-else construction.
        - Run nodes of children followed child_if or child_else.
        - When the flow of child_if or child_else is finished, then run children of if node.
      parameters:
        condition:
          description:
            - The condition that determines the execution path in a conditional branch.
        child_if:
          description:
            - Reference to the node to be processed if the condition parameter evaluates to True.
        child_else:
          description:
            - Reference to the node to be processed if the condition parameter evaluates to False.
    EXAMPLE: |-
      # Print true if flowdata['cond'] is OK else print false.
      # Parent node can be set with parent field as <node name>.<field name>
      #     ┌─> true message  ─┐
      # if ─┤                  ├─> out
      #     └─> false message ─┘
      # Output: No output
      - if:
          name: "if"
          condition: "fd.cond == 'OK'"
      - message:
          name: "true message"
          msg: "true"
          out_field: "message"
          parent: "if.child_if"
      - message:
          name: "false message"
          msg: "false"
          out_field: "message"
          parent: "if.child_else"
      - stdout:
          name: "out"
          src: "{{ fd.message }}"
          parent: "if"

      # This example behaves in the same way as the one above.
      #     ┌─> true message  ──> out true
      # if ─┤
      #     └─> false message ──> out false
      - if:
          name: "if"
          condition: "macro.cond == 'OK'"
      - message:
          name: "true message"
          msg: "true"
          parent: "if.child_if"
      - stdout:
          name: "out true"
          src: "{{ fd['true message'] }}"
      - message:
          name: "false message"
          msg: "false"
          parent: "if.child_else"
      - stdout:
          name: "out false"
          src: "{{ fd['false message'] }}"
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.cond: Variable | None = None
        self.if_children: TypeChild = {"child_if": None, "child_else": None}

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "condition": ArgSpec(type="expression", required=True),
            "child_if": ArgSpec(type="node", required=False, default=None),
            "child_else": ArgSpec(type="node", required=False, default=None),
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
