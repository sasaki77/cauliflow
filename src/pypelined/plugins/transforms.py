from copy import deepcopy
from functools import singledispatchmethod

from pypelined.blackboard import bb
from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("dict_keys")
class DictKeysNode(ProcessNode):
    def __init__(self, name, input, out_bb=False):
        super().__init__(name)
        self.input: dict = Variable(input)
        self.out_bb = out_bb

    async def process(self, flowdata: FlowData):
        dikt = self.input.fetch(flowdata)
        out = list(dikt.keys())
        if self.out_bb:
            _bb = bb.get()
            _bb[self.name] = out
        else:
            flowdata[self.name] = out
        return flowdata


@node.register("dict_values")
class DictValuesNode(ProcessNode):
    def __init__(self, name, input, out_bb=False):
        super().__init__(name)
        self.input: dict = Variable(input)
        self.out_bb = out_bb

    async def process(self, flowdata: FlowData):
        dikt = self.input.fetch(flowdata)
        out = list(dikt.values())
        if self.out_bb:
            _bb = bb.get()
            _bb[self.name] = out
        else:
            flowdata[self.name] = out
        return flowdata


@node.register("concat")
class ConcatNode(ProcessNode):
    def __init__(self, name, first, second, out_bb=False):
        super().__init__(name)
        self.first: dict = Variable(first)
        self.second: dict = Variable(second)
        self.out_bb = out_bb

    async def process(self, flowdata: FlowData):
        first = self.first.fetch(flowdata)
        second = self.second.fetch(flowdata)
        out = self._concat(first, second)
        if self.out_bb:
            _bb = bb.get()
            _bb[self.name] = out
        else:
            flowdata[self.name] = out
        return flowdata

    def _concat(self, first, second):
        is_1st_list = isinstance(first, list)
        is_2nd_list = isinstance(second, list)

        if is_1st_list and is_2nd_list:
            min_len = min(len(first), len(second))
            out = []
            for i in range(min_len):
                out.append(first[i] + second[i])
            return out

        if is_1st_list:
            return [fl + second for fl in first]

        if is_2nd_list:
            return [first + sl for sl in second]

        return first + second


@node.register("mutate")
class MutateNode(ProcessNode):
    def __init__(
        self,
        name,
        target: str = None,
        split: dict = {},
        copy: dict = {},
        out_bb: bool = False,
    ):
        super().__init__(name)
        self.out_bb = out_bb
        self.split_dict = split
        self.copy_dict = copy
        self.target = Variable(target)

    async def process(self, flowdata: FlowData):
        target = self.target.fetch(flowdata)
        target = deepcopy(target)
        self.apply(target)
        if self.out_bb:
            _bb = bb.get()
            bb[self.name] = target
        else:
            flowdata[self.name] = target
        return flowdata

    @singledispatchmethod
    def apply(self, target):
        self.copy(target)
        self.split(target)

    @apply.register
    def _(self, targets: list):
        for target in targets:
            self.apply(target)

    def split(self, target):
        for field, parser in self.split_dict.items():
            target[field] = target[field].split(parser)

    def copy(self, target):
        for src, dst in self.copy_dict.items():
            target[dst] = deepcopy(target[src])
