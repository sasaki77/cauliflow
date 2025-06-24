import asyncio
from collections.abc import Iterable
from enum import StrEnum
from typing import TypedDict

from cauliflow.context import ctx_flowdata, init_flowdata
from cauliflow.flowdata import FlowData
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


class ForEachMode(StrEnum):
    SEQUENTIAL = "sequential"
    CONCURRENT = "concurrent"


@node.register("foreach")
class ForEachNode(FlowControlNode):
    """
    DOCUMENTATION:
      short_description: Run the child node for each item in the list of data.
      description:
        - Run the child node for each item in the list of data.
        - The child node can be called either sequentially or concurrently.
        - The item in the list is passed within the flowdata.
        - When the flow of child_for is finished, then run children of foreach node.
      parameters:
        mode:
          description:
            - Set either of sequential or concurrent.
        items:
          description:
            - List of elements to be processed one by one by the child node.
        item_name:
          description:
            - Key name of passed item in the flowdata.
        child_for:
          description:
            - Child node to be run for each item.
    EXAMPLE: |-
      # Print 1, 2, 3, and hello into the stdout
      # Output: No output
      - foreach:
          name: "for"
          items: [1, 2, 3]
          item_name: "foo"
          mode: "sequential"
      - stdout:
          name: "out_for"
          src: "{{ fd.foo }}"
          parent: "for.child_for"
      - stdout:
          name: "out"
          src: "hello"
          parent: "for"
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.child_for: Node | None = None

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "mode": ArgSpec(type="str", required=False, default=ForEachMode.CONCURRENT),
            "items": ArgSpec(type="list", required=True),
            "item_name": ArgSpec(type="str", required=False, default="item"),
            "child_for": ArgSpec(type="node", required=False, default=None),
        }

    async def process(self) -> None:
        if self.child_for is None:
            return

        items = self.params["items"]
        if not isinstance(items, Iterable):
            raise ValueError("items is not Iterable")

        mode = self.params["mode"]
        item_name = self.params["item_name"]

        base_fd = ctx_flowdata.get()

        if mode == ForEachMode.SEQUENTIAL:
            await self._sequential(base_fd, items, item_name, self.child_for)
        elif mode == ForEachMode.CONCURRENT:
            await self._concurrent(base_fd, items, item_name, self.child_for)
        else:
            raise ValueError(f"{mode} is not valid mode")

        ctx_flowdata.set(base_fd)

    def add_child(self, child: Node, param: str | None = None) -> None:
        if param is None:
            self.child = child
            return

        if param != "child_for":
            _logger.warning(f"{param} is invalid field")

        self.child_for = child

    async def _sequential(self, base_fd, items, item_name, child: Node):
        for item in items:
            init_flowdata()
            fd = ctx_flowdata.get()
            fd.update(base_fd)
            fd[item_name] = item
            await child.run()

    async def _concurrent(self, base_fd, items, item_name, child: Node):
        async with asyncio.TaskGroup() as tg:
            for item in items:
                init_flowdata()
                fd = ctx_flowdata.get()
                fd.update(base_fd)
                fd[item_name] = item
                tg.create_task(child.run())


@node.register("dispatch")
class DispatchNode(FlowControlNode):
    """
    DOCUMENTATION:
      short_description: Dispatch the flowdata to the target nodes.
      description:
        - Dispatch the flowdata to the flows of target nodes.
        - The target nodes can be called either sequentially or concurrently.
        - The flowdata is shared in sequential mode.
        - The flowdata is finally merged and passed to the child node in concurrent mode.
        - When the flows of the target nodes are finished, then run children of dispatch node.
      parameters:
        mode:
          description:
            - Set either of sequential or concurrent.
        targets:
          description:
            - Target nodes to dispatch the flowdata.
    EXAMPLE: |-
      # Dispatch the flowdata sequentially
      # Output: {'msg': 10, 'target1': 11, 'target2': 21, 'target3': 31}
      - message:
          name: "msg"
          msg: 10
      - dispatch:
          name: "dispatch"
          mode: "sequential"
      - message:
          name: "target1"
          msg: "{{ fd.msg + 1 }}"
          parent: "dispatch.targets"
      - message:
          name: "target2"
          msg: "{{ fd.msg + fd.target1 }}"
          parent: "dispatch.targets"
      - message:
          name: "target3"
          msg: "{{ fd.msg + fd.target2 }}"
          parent: "dispatch.targets"

      # Dispatch the flowdata concurrently
      # Output: {'msg': 10, 'target1': 11, 'target2': 12, 'target3': 13}
      - message:
          name: "msg"
          msg: 10
      - dispatch:
          name: "dispatch"
          mode: "concurrent"
      - message:
          name: "target1"
          msg: "{{ fd.msg + 1 }}"
          parent: "dispatch.targets"
      - message:
          name: "target2"
          msg: "{{ fd.msg + 2 }}"
          parent: "dispatch.targets"
      - message:
          name: "target3"
          msg: "{{ fd.msg + 3 }}"
          parent: "dispatch.targets"
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.targets: list[Node] = []

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "mode": ArgSpec(type="str", required=False, default=ForEachMode.CONCURRENT),
            "targets": ArgSpec(type="list(node)", required=False, default=None),
        }

    async def process(self) -> None:
        if len(self.targets) < 1:
            _logger.warning("dispatch is called, but it has no target.")
            return

        mode = self.params["mode"]

        if mode == ForEachMode.SEQUENTIAL:
            await self._sequential(self.targets)
        elif mode == ForEachMode.CONCURRENT:
            base_fd = ctx_flowdata.get()
            fd = await self._concurrent(base_fd, self.targets)
            ctx_flowdata.set(fd)
        else:
            raise ValueError(f"{mode} is not valid mode")

    def add_child(self, child: Node, param: str | None = None) -> None:
        if param is None:
            self.child = child
            return

        if param != "targets":
            _logger.warning(f"{param} is invalid field")

        self.targets.append(child)

    async def _sequential(self, targets: list[Node]) -> None:
        for target in targets:
            await target.run()

    async def _concurrent(self, base_fd, targets: list[Node]) -> FlowData:
        fds = []
        async with asyncio.TaskGroup() as tg:
            for target in targets:
                init_flowdata()
                fd = ctx_flowdata.get()
                fds.append(fd)
                fd.update(base_fd)
                tg.create_task(target.run())
        ret = {}
        for fd in fds:
            ret.update(fd)
        return FlowData(ret)
