from copy import deepcopy
from functools import singledispatchmethod

from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("dict_keys")
class DictKeysNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "input": ArgSpec(type="dict", required=True),
        }

    async def process(self) -> None:
        input = self.params["input"]
        out = list(input.keys())
        self.output(out)


@node.register("dict_values")
class DictValuesNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "input": ArgSpec(type="dict", required=True),
        }

    async def process(self) -> None:
        input = self.params["input"]
        out = list(input.values())
        self.output(out)


@node.register("concat")
class ConcatNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "first": ArgSpec(type="any", required=True),
            "second": ArgSpec(type="any", required=True),
        }

    async def process(self) -> None:
        first = self.params["first"]
        second = self.params["second"]
        out = self._concat(first, second)
        self.output(out)

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
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "target": ArgSpec(type="any", required=True),
            "split": ArgSpec(type="dict", required=False, default={}),
            "copy": ArgSpec(type="dict", required=False, default={}),
        }

    async def process(self) -> None:
        target = self.params["target"]
        target = deepcopy(target)
        self.apply(target)
        self.output(target)

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
