from functools import singledispatchmethod

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node
from cauliflow.variable import Variable

_logger = get_logger(__name__)


@node.register("for_list")
class ForList(ProcessNode):
    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.variable = None
        self.filter = None

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "lists": ArgSpec(type="list", required=True),
            "expression": ArgSpec(type="str", required=True),
            "filter": ArgSpec(type="str", required=False, default=None),
        }

    async def process(self) -> None:
        if self.variable is None:
            self.variable = Variable("{{" + self.params["expression"] + "}}")
        if self.filter is None and self.params["filter"] is not None:
            self.filter = Variable("{{" + self.params["filter"] + "}}")

        lists = self.params["lists"]
        var_dict = {}
        items = self._for_loop(lists[0], 0, lists[1:], self.variable, var_dict)
        self.output(items)

    @singledispatchmethod
    def _for_loop(
        self, item, i: int, lists: list, variable: Variable, var_dict: dict
    ) -> list:
        _logger.critical("lists must be list or dict")
        return []

    @_for_loop.register
    def _(
        self, forlist: list, i: int, lists: list, variable: Variable, var_dict: dict
    ) -> list:
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
        print(items)
        return items

    @_for_loop.register
    def _(
        self, fordict: dict, i: int, lists: list, variable: Variable, var_dict: dict
    ) -> list:
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
    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.key = None
        self.val = None
        self.filter = None

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "lists": ArgSpec(type="list", required=True),
            "key": ArgSpec(type="str", required=True),
            "val": ArgSpec(type="str", required=True),
            "filter": ArgSpec(type="str", required=False, default=None),
        }

    async def process(self) -> None:
        if self.key is None:
            self.key = Variable("{{" + self.params["key"] + "}}")
        if self.val is None:
            self.val = Variable("{{" + self.params["val"] + "}}")
        if self.filter is None and self.params["filter"] is not None:
            self.filter = Variable("{{" + self.params["filter"] + "}}")

        lists = self.params["lists"]
        var_dict = {}
        items = self._for_loop(lists[0], 0, lists[1:], self.key, self.val, var_dict)
        self.output(items)

    @singledispatchmethod
    def _for_loop(
        self, item, i: int, lists: list, key: Variable, val: Variable, var_dict: dict
    ) -> dict:
        _logger.critical("lists must be list or dict")
        return {}

    @_for_loop.register
    def _(
        self,
        forlist: list,
        i: int,
        lists: list,
        key: Variable,
        val: Variable,
        var_dict: dict,
    ) -> dict:
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
        self,
        fordict: dict,
        i: int,
        lists: list,
        key: Variable,
        val: Variable,
        var_dict: dict,
    ) -> dict:
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
