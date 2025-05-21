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

    DOCUMENTATION = r"""
    short_description: Output the list of the keys in dict.
    description:
      - Output the list of the keys in dict.
    parameters:
      input:
        description:
          - dict data to get the keys.
    """

    EXAMPLES = r"""
# Output the list of the keys in dict to flowdata.
# Output: {'keys': ['key1', 'key2']}
- dict_keys:
    name: "keys"
    input:
      key1: 1
      key2: 2

# Output the list of the keys in dict to flowdata.
# Input: {'dict_data': {'key1': 'foo', 'key2': 'bar'}}
# Output: {'keys': ['key1', 'key2']}
- dict_keys:
    name: "keys"
    input: "{{ flowdata['dict_data'] }}"

# Output the list of the keys in dict to blackboard.
# Output: {'foo': ['key1', 'key2']}
- dict_keys:
    name: "keys"
    input:
      key1: 1
      key2: 2
    out_bb: yes
    out_field: "foo"
    """


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

    DOCUMENTATION = r"""
    short_description: Output the list of the values in dict.
    description:
      - Output the list of the values in dict.
    parameters:
      input:
        description:
          - dict data to get the values.
    """

    EXAMPLES = r"""
# Output the list of the values in dict to flowdata.
# Output: {'values': [1, 2]}
- dict_values:
    name: "values"
    input:
      key1: 1
      key2: 2

# Output the list of the values in dict to flowdata.
# Input: {'dict_data': {'key1': 'foo', 'key2': 'bar'}}
# Output: {'values': ['foo', 'bar']}
- dict_values:
    name: "values"
    input: "{{ flowdata['dict_data'] }}"

# Output the list of the values in dict to blackboard.
# Output: {'foo': [1, 2]}
- dict_values:
    name: "values"
    input:
      key1: 1
      key2: 2
    out_bb: yes
    out_field: "foo"
    """


@node.register("concat")
class ConcatNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "first": ArgSpec(type="str|list[str]", required=True),
            "second": ArgSpec(type="str|list[str]", required=True),
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

    DOCUMENTATION = r"""
    short_description: Concatenate strings.
    description:
      - Concatenate strings.
      - list of string can be passed.
    parameters:
      first:
        description:
          - string or list of strings to be concatnate before second parameter
      second:
        description:
          - string or list of strings to be concatnate after first parameter
    """

    EXAMPLES = r"""
# Concatenate the 2 strings.
# Output: {'concat': 'head1:pv1'}
- concat:
    name: "concat"
    first: "head1:"
    second: "pv1"

# Concatenate the 1 string and 1 list of string.
# Output: {'concat': ['head1:pv1', 'head1:pv2']}
- concat:
    name: "concat"
    first: "head1:"
    second: ["pv1", "pv2"]

# Concatenate the 2 list of string.
# Output: {'concat': ['head1:pv1', 'head2:pv2']}
- concat:
    name: "concat"
    first: ["head1:", "head2:"]
    second: ["pv1", "pv2"]

# Concatenate the 2 list of string, but length is different.
# Output: {'concat': ['head1:pv1', 'head2:pv2']}
- concat:
    name: "concat"
    first: ["head1:", "head2:", "head3:"]
    second: ["pv1", "pv2"]

# Concatenate the 2 strings and output to the blackboard.
# Output: {'foo': 'head1:pv1'}
- concat:
    name: "concat"
    first: "head1:"
    second: "pv1"
    out_bb: yes
    out_field: "foo"
    """


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
