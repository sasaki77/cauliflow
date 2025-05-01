import logging
from functools import singledispatchmethod

from pypelined.blackboard import bb
from pypelined.flowdata import fd
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable

_logger = logging.getLogger(__name__)


@node.register("for_list")
class ForList(ProcessNode):
    def __init__(self, name, lists: list, expression: str, filter=None, out_bb=False):
        super().__init__(name)
        self.variable = Variable(expression)
        self.lists = Variable(lists)
        self.filter = Variable(filter) if filter else None
        self.out_bb = out_bb

    async def process(self):
        lists = self.lists.fetch()
        var_dict = {}
        items = self._for_loop(lists[0], 0, lists[1:], self.variable, var_dict)
        if self.out_bb:
            _bb = bb.get()
            _bb[self.name] = items
        else:
            flowdata = fd.get()
            flowdata[self.name] = items
        return

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
                if self.filter is not None and self.filter.fetch(extend=var_dict):
                    continue
                ret = variable.fetch(extend=var_dict)
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
                if self.filter is not None and self.filter.fetch(extend=var_dict):
                    continue
                ret = variable.fetch(extend=var_dict)
                items.append(ret)
        return items


@node.register("for_dict")
class ForDict(ProcessNode):
    def __init__(
        self, name, lists: list, key: str, val: str, filter=None, out_bb=False
    ):
        super().__init__(name)
        self.key = Variable(key)
        self.val = Variable(val)
        self.lists = Variable(lists)
        self.filter = Variable(filter) if filter else None
        self.out_bb = out_bb

    async def process(self):
        lists = self.lists.fetch()
        var_dict = {}
        items = self._for_loop(lists[0], 0, lists[1:], self.key, self.val, var_dict)
        if self.out_bb:
            _bb = bb.get()
            _bb[self.name] = items
        else:
            flowdata = fd.get()
            flowdata[self.name] = items
        return

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
                if self.filter is not None and self.filter.fetch(extend=var_dict):
                    continue
                _key = key.fetch(extend=var_dict)
                _val = val.fetch(extend=var_dict)
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
                if self.filter is not None and self.filter.fetch(extend=var_dict):
                    continue
                _key = key.fetch(extend=var_dict)
                _val = val.fetch(extend=var_dict)
                items[_key] = _val
        return items
