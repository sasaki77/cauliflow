import logging
from functools import singledispatchmethod

from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable

_logger = logging.getLogger(__name__)


@node.register("for_list")
class ForList(ProcessNode):
    def __init__(self, _bb, name, lists: list, expression: str, filter=None):
        super().__init__(_bb, name)
        self.variable = Variable(expression, _bb)
        self.lists = Variable(lists, _bb)
        self.filter = Variable(filter, _bb) if filter else None

    async def process(self, flowdata: FlowData) -> FlowData:
        lists = self.lists.fetch(flowdata)
        var_dict = {"fd": FlowData}
        items = self._for_loop(lists[0], 0, lists[1:], self.variable, var_dict)
        flowdata[self.name] = items
        return flowdata

    @singledispatchmethod
    def _for_loop(self, item, i: int, lists: list, variable: Variable, var_dict: dict):
        _logger.critical("lists must be list or dict")

    @_for_loop.register
    def _(self, forlist: list, i: int, lists: list, variable: Variable, var_dict):
        items = []
        for item in forlist:
            var_dict[f"item{i}"] = item
            if len(lists) > 0:
                ret = self._for_loop(lists[0], i + 1, lists[1:], variable, var_dict)
                items.extend(ret)
            else:
                if self.filter is not None and self.filter.fetch(None, extend=var_dict):
                    continue
                ret = variable.fetch(None, extend=var_dict)
                items.append(ret)
        return items

    @_for_loop.register
    def _(self, fordict: dict, i: int, lists: list, variable: Variable, var_dict):
        items = []
        for key, item in fordict.items():
            var_dict[f"item{i}_key"] = key
            var_dict[f"item{i}_item"] = item
            if len(lists) > 0:
                ret = self._for_loop(lists[0], i + 1, lists[1:], variable, var_dict)
                items.extend(ret)
            else:
                if self.filter is not None and self.filter.fetch(None, extend=var_dict):
                    continue
                ret = variable.fetch(None, extend=var_dict)
                items.append(ret)
        return items


@node.register("for_dict")
class ForDict(ProcessNode):
    def __init__(self, _bb, name, lists: list, key: str, val: str, filter=None):
        super().__init__(_bb, name)
        self.key = Variable(key, _bb)
        self.val = Variable(val, _bb)
        self.lists = Variable(lists, _bb)
        self.filter = Variable(filter, _bb) if filter else None

    async def process(self, flowdata: FlowData) -> FlowData:
        lists = self.lists.fetch(flowdata)
        var_dict = {"fd": FlowData}
        items = self._for_loop(lists[0], 0, lists[1:], self.key, self.val, var_dict)
        flowdata[self.name] = items
        return flowdata

    @singledispatchmethod
    def _for_loop(
        self, item, i: int, lists: list, key: Variable, val: Variable, var_dict: dict
    ):
        _logger.critical("lists must be list or dict")

    @_for_loop.register
    def _(
        self, forlist: list, i: int, lists: list, key: Variable, val: Variable, var_dict
    ):
        items = {}
        for item in forlist:
            var_dict[f"item{i}"] = item
            if len(lists) > 0:
                ret = self._for_loop(lists[0], i + 1, lists[1:], key, val, var_dict)
                items.update(ret)
            else:
                if self.filter is not None and self.filter.fetch(None, extend=var_dict):
                    continue
                _key = key.fetch(None, extend=var_dict)
                _val = val.fetch(None, extend=var_dict)
                items[_key] = _val
        return items

    @_for_loop.register
    def _(
        self, fordict: dict, i: int, lists: list, key: Variable, val: Variable, var_dict
    ):
        items = {}
        for ikey, ival in fordict.items():
            var_dict[f"item{i}_key"] = ikey
            var_dict[f"item{i}_val"] = ival
            if len(lists) > 0:
                ret = self._for_loop(lists[0], i + 1, lists[1:], key, val, var_dict)
                items.update(ret)
            else:
                if self.filter is not None and self.filter.fetch(None, extend=var_dict):
                    continue
                _key = key.fetch(None, extend=var_dict)
                _val = val.fetch(None, extend=var_dict)
                items[_key] = _val
        return items
