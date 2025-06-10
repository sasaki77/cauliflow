from functools import singledispatchmethod

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node
from cauliflow.variable import Variable

_logger = get_logger(__name__)


@node.register("for_list")
class ForList(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Loop the list of list or dict and create a new list to output.
      description:
        - Loop the list of list or dict and create a new list to output.
      parameters:
        lists:
          description:
            - List of list or dict to make a nested loop.
            - Single list or dict can be passed.
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
    EXAMPLE: |-
      # Create a list from list of list with filter parameter.
      # Output: {'for_list': [3, 4, 6]}
      - for_list:
          name: "for_list"
          lists: [[1, 2], [3, 4]]
          expression: "item0*item1"
          filter: "item0*item1>7"

      # Create a list from list of list and dict.
      # Output: {'for_list': ['head1:val1', 'head1:val2', 'head2:val1', 'head2:val2']}
      - for_list:
          name: "for_list"
          lists: [["head1", "head2"], {"name1": "val1", "name2": "val2"}]
          expression: "item0 + ':' + item1_val"

      # Create a list from a single list.
      # Output: {'for_list': [2, 4, 6]}
      - for_list:
          name: "for_list"
          lists: [1, 2, 3, 4]
          expression: "item0*2"
          filter: "item0*2>7"

      # Create a list from a dict.
      # Output: {'for_list': ["key1-1", "key2-2"]}
      - for_list:
          name: "for_list"
          lists: {"key1": 1, "key2": 2}
          expression: "item0_key + '-' + item0_val | str"

      # Create a list from nested lists of a dict.
      # Output: {'for_list': ["hello, world", "foobar"]}
      - for_list:
          name: "for_list"
          lists: [[{"first": "hello, ", "second": "world"}, {"first": "foo", "second": "bar"}]]
          expression:  "item0.first + item0.second"
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.variable = None
        self.filter = None

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "lists": ArgSpec(type="list[list|dict]", required=True),
            "expression": ArgSpec(type="expression", required=True),
            "filter": ArgSpec(type="expression", required=False, default=None),
        }

    async def process(self) -> None:
        if self.variable is None:
            self.variable = Variable("{{" + self.params["expression"] + "}}")
        if self.filter is None and self.params["filter"] is not None:
            self.filter = Variable("{{" + self.params["filter"] + "}}")

        lists = self.params["lists"]
        is_dict = isinstance(lists, dict)

        if is_dict:
            items = self._for_loop(lists, 0, [], {})
            self.output(items)
            return

        if not isinstance(lists, list):
            raise ValueError

        if len(lists) < 1:
            return

        has_list_or_dict = isinstance(lists[0], (list, dict))
        loop_lists = lists if has_list_or_dict else [lists]

        items = self._for_loop(loop_lists[0], 0, loop_lists[1:], {})
        self.output(items)

    @singledispatchmethod
    def _for_loop(
        self, iterable, depth: int, remaining_lists: list, var_dict: dict
    ) -> list:
        _logger.critical("Input must be a list or dict")
        return []

    @_for_loop.register
    def _(
        self, for_list: list, depth: int, remaining_lists: list, var_dict: dict
    ) -> list:
        self._validate_variable()

        results = []
        for item in for_list:
            var_dict[f"item{depth}"] = item
            results.extend(self._process_next_level(depth, remaining_lists, var_dict))
        return results

    @_for_loop.register
    def _(
        self, for_dict: dict, depth: int, remaining_lists: list, var_dict: dict
    ) -> list:
        self._validate_variable()

        results = []
        for key, value in for_dict.items():
            var_dict[f"item{depth}_key"] = key
            var_dict[f"item{depth}_val"] = value
            results.extend(self._process_next_level(depth, remaining_lists, var_dict))
        return results

    def _process_next_level(
        self, depth: int, remaining_lists: list, var_dict: dict
    ) -> list:
        if remaining_lists:
            return self._for_loop(
                remaining_lists[0], depth + 1, remaining_lists[1:], var_dict
            )
        if self.filter and self.filter.fetch(extend=var_dict):
            return []
        return [self.variable.fetch(extend=var_dict)]  # type: ignore

    def _validate_variable(self):
        if self.variable is None:
            raise ValueError("Variable is not set.")


@node.register("for_dict")
class ForDict(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Loop the list of list or dict and create a new dict to output.
      description:
        - Loop the list of list or dict and create a new dict to output.
      parameters:
        lists:
          description:
            - List of list or dict to make a nested loop.
            - Single list or dict can be passed.
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
    EXAMPLE: |-
      # Create a dict from list of list and dict.
      # Output: {'for_dict': {'head1:name1': 'val1', 'head1:name2': 'val2', 'head2:name1': 'val1', 'head2:name2': 'val2'}}
      - for_dict:
          name: "for_dict"
          lists: [["head1", "head2"], {"name1": "val1", "name2": "val2"}]
          key: "item0 + ':' + item1_key"
          val: "item1_val"

      # Create a dict from a single list.
      # Output: {'for_dict': {"key1": 2, "key2": 4, "key3": 6}}
      - for_dict:
          name: "for_dict"
          lists: [1, 2, 3, 4]
          key: "'key' + item0 |str"
          val: "item0*2"
          filter: "item0*2>7"

      # Create a dict from a dict.
      # Output: {'for_dict': {"key1-1": 1, "key2-2": 2}}
      - for_dict:
          name: "for_dict"
          lists: {"key1": 1, "key2": 2}
          key: "item0_key + '-' + item0_val | str"
          val: "item0_val"
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
            "key": ArgSpec(type="expression", required=True),
            "val": ArgSpec(type="expression", required=True),
            "filter": ArgSpec(type="expression", required=False, default=None),
        }

    async def process(self) -> None:
        if self.key is None:
            self.key = Variable("{{" + self.params["key"] + "}}")
        if self.val is None:
            self.val = Variable("{{" + self.params["val"] + "}}")
        if self.filter is None and self.params["filter"] is not None:
            self.filter = Variable("{{" + self.params["filter"] + "}}")

        lists = self.params["lists"]
        is_dict = isinstance(lists, dict)

        if is_dict:
            items = self._for_loop(lists, 0, [], {})
            self.output(items)
            return

        if not isinstance(lists, list):
            raise ValueError

        if len(lists) < 1:
            return

        has_list_or_dict = isinstance(lists[0], (list, dict))
        loop_lists = lists if has_list_or_dict else [lists]

        items = self._for_loop(loop_lists[0], 0, loop_lists[1:], {})
        self.output(items)

    @singledispatchmethod
    def _for_loop(
        self, iterable, depth: int, remaining_lists: list, var_dict: dict
    ) -> dict:
        _logger.critical("Input must be a list or dict")
        return {}

    @_for_loop.register
    def _(
        self, for_list: list, depth: int, remaining_lists: list, var_dict: dict
    ) -> dict:
        self._validate_variable()

        results = {}
        for item in for_list:
            var_dict[f"item{depth}"] = item
            results.update(self._process_next_level(depth, remaining_lists, var_dict))
        return results

    @_for_loop.register
    def _(
        self, for_dict: dict, depth: int, remaining_lists: list, var_dict: dict
    ) -> dict:
        self._validate_variable()

        results = {}
        for key, value in for_dict.items():
            var_dict[f"item{depth}_key"] = key
            var_dict[f"item{depth}_val"] = value
            results.update(self._process_next_level(depth, remaining_lists, var_dict))
        return results

    def _process_next_level(
        self, depth: int, remaining_lists: list, var_dict: dict
    ) -> dict:
        if remaining_lists:
            return self._for_loop(
                remaining_lists[0], depth + 1, remaining_lists[1:], var_dict
            )
        if self.filter and self.filter.fetch(extend=var_dict):
            return {}
        _key = self.key.fetch(extend=var_dict)  # type: ignore
        _val = self.val.fetch(extend=var_dict)  # type: ignore
        return {_key: _val}

    def _validate_variable(self):
        if self.key is None or self.val is None:
            raise ValueError("Variable is not set.")
