from functools import singledispatchmethod

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node
from cauliflow.variable import Variable

_logger = get_logger(__name__)


@node.register("for_list")
class ForList(ProcessNode):
    DOCUMENTATION = r"""
    short_description: Loop the list of list or dict and create a new list to output.
    description:
      - Loop the list of list or dict and create a new list to output.
    parameters:
      lists:
        description:
          - List of list or dict to make a nested loop.
      expression:
        description:
          - Expression of a item for a created list.
          - Item in the loop of list can be referred as item*.
          - Item in the loop of dict can be referred as item*_val and item*_key.
          - For the first loop item can be referred as item0.
          - For the second loop item can be referred as item1.
      filter:
        description:
          - Condition not to add item for a crated list.
          - Loop item can be refereed as same as in expression.
    """

    EXAMPLES = r"""
# Create a list from list of list with filter parameter.
# Output: {'for_list': [3, 4, 6]}
- for_list:
    name: "for_list"
    lists: [[1, 2], [3, 4]]
    expression: "item0*item1"
    filter: "item0*item1>7"

# Create a list from list of list and dict
# Output: {'for_list': ['head1:val1', 'head1:val2', 'head2:val1', 'head2:val2']}
- for_list:
    name: "for_list"
    lists: [["head1", "head2"], {"name1": "val1", "name2": "val2"}]
    expression: "item0 + ':' + item1_val"
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.variable = None
        self.filter = None

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "lists": ArgSpec(type="list[list|dict]", required=True),
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
        return items

    @_for_loop.register
    def _(
        self, fordict: dict, i: int, lists: list, variable: Variable, var_dict: dict
    ) -> list:
        items = []
        for key, item in fordict.items():
            var_dict[f"item{i}_key"] = key
            var_dict[f"item{i}_val"] = item
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
    DOCUMENTATION = r"""
    short_description: Loop the list of list or dict and create a new dict to output.
    description:
      - Loop the list of list or dict and create a new dict to output.
    parameters:
      lists:
        description:
          - List of list or dict to make a nested loop.
      key:
        description:
          - Expression of a item of key for a created dict.
          - Item in the loop of list can be referred as item*.
          - Item in the loop of dict can be referred as item*_val and item*_key.
          - For the first loop item can be referred as item0.
          - For the second loop item can be referred as item1.
      val:
        description:
          - Expression of of a item of value for a created dict.
          - Loop item can be refereed as same as in key.
      filter:
        description:
          - Condition not to add item for a crated dict.
          - Loop item can be refereed as same as in expression.
    """

    EXAMPLES = r"""
# Create a dict from list of list and dict
# Output: {'for_dict': {'head1:name1': 'val1', 'head1:name2': 'val2', 'head2:name1': 'val1', 'head2:name2': 'val2'}}
- for_dict:
    name: "for_dict"
    lists: [["head1", "head2"], {"name1": "val1", "name2": "val2"}]
    key: "item0 + ':' + item1_key"
    val: "item1_val"
    """

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
