from copy import deepcopy
from functools import singledispatchmethod

from pypelined.context import ctx_blackboard, ctx_flowdata
from pypelined.node import ArgumentSpec, ProcessNode, node


@node.register("dict_keys")
class DictKeysNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "input": {"type": "dict", "required": True},
            "out_bb": {"type": "bool", "required": False, "default": False},
        }

    async def process(self) -> None:
        input = self.params["input"]
        out = list(input.keys())

        outbb = self.params["out_bb"]
        if outbb:
            _bb = ctx_blackboard.get()
            _bb[self.name] = out
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = out


@node.register("dict_values")
class DictValuesNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "input": {"type": "dict", "required": True},
            "out_bb": {"type": "bool", "required": False, "default": False},
        }

    async def process(self) -> None:
        input = self.params["input"]
        out = list(input.values())

        outbb = self.params["out_bb"]
        if outbb:
            _bb = ctx_blackboard.get()
            _bb[self.name] = out
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = out


@node.register("concat")
class ConcatNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "first": {"type": "any", "required": True},
            "second": {"type": "any", "required": True},
            "out_bb": {"type": "bool", "required": False, "default": False},
        }

    async def process(self) -> None:
        first = self.params["first"]
        second = self.params["second"]
        out = self._concat(first, second)

        outbb = self.params["out_bb"]
        if outbb:
            _bb = ctx_blackboard.get()
            _bb[self.name] = out
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = out
        return

    def _concat(
        self, first: str | list[str], second: str | list[str]
    ) -> str | list[str]:
        is_1st_list = isinstance(first, list)
        is_2nd_list = isinstance(second, list)

        if is_1st_list and is_2nd_list:
            min_len = min(len(first), len(second))
            out = []
            for i in range(min_len):
                out.append(first[i] + second[i])
            return out

        if is_1st_list:
            return [fl + second for fl in first]  # type: ignore

        if is_2nd_list:
            return [first + sl for sl in second]  # type: ignore

        return first + second


@node.register("mutate")
class MutateNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "target": {"type": "any", "required": True},
            "split": {"type": "dict", "required": False, "default": {}},
            "copy": {"type": "dict", "required": False, "default": {}},
            "out_bb": {"type": "bool", "required": False, "default": False},
        }

    async def process(self) -> None:
        target = self.params["target"]
        target = deepcopy(target)
        self.apply(target)
        outbb = self.params["out_bb"]
        if outbb:
            _bb = ctx_blackboard.get()
            _bb[self.name] = target
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = target

    @singledispatchmethod
    def apply(self, target: dict):
        self.copy(target)
        self.split(target)

    @apply.register
    def _(self, targets: list) -> None:
        for target in targets:
            self.apply(target)

    def split(self, target) -> None:
        split_dict = self.params["split"]
        for field, parser in split_dict.items():
            target[field] = target[field].split(parser)

    def copy(self, target):
        copy_dict = self.params["copy"]
        for src, dst in copy_dict.items():
            target[dst] = deepcopy(target[src])
