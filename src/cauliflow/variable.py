from functools import partial
from operator import contains
from typing import Any

from lark import Lark, ParseTree, Transformer, Tree, v_args

from cauliflow.context import ctx_blackboard, ctx_flowdata, ctx_macros
from cauliflow.filters import FILTERS

_grammar = r"""
    start: (text | expression_wrapper)*
    text: /[^{}]+/
    expression_wrapper: "{{" expression "}}"
    ?expression: disjunction

    ?disjunction: conjunction
        | conjunction "or" conjunction -> or_

    ?conjunction: inversion
        | inversion "and" inversion -> and_

    ?inversion: comparison
        | "not" inversion -> not_

    ?comparison: sum
        | comparison "<" sum        -> lt
        | comparison ">" sum        -> gt
        | comparison "==" sum       -> eq
        | comparison "!=" sum       -> ne
        | comparison ">=" sum       -> ge
        | comparison "<=" sum       -> le
        | comparison "in" sum       -> contains_
        | comparison "not in" sum   -> not_contains
        | comparison "is" sum       -> is_
        | comparison "is not" sum   -> is_not

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom_expr
        | product "*" atom_expr  -> mul
        | product "/" atom_expr  -> div
        | product "//" atom_expr -> floor
        | product "%" atom_expr  -> mod

    ?atom_expr: atom
        | atom_expr "[" index "]" -> getitem
        | atom_expr "." NAME      -> getitem
        | atom_expr "|" filter    -> filter

    filter: NAME [arguments_wrapper] -> filter_func

    arguments_wrapper: "(" [arguments] ")" -> arguments_wrapper
    arguments: [arg ("," arg)*] -> arguments
    arg: expression -> arg

    ?index: expression
        | slice

    slice: expression ":" expression

    ?atom: number
        | "-" atom         -> neg
        | NAME             -> var
        | "True"           -> true
        | "False"          -> false
        | "None"           -> none
        | string
        | list
        | dict
        | "(" disjunction ")"

    ?number: INT    -> integer
        | FLOAT     -> float

    string: STRING

    list: "[" [disjunction ("," disjunction)*] "]"
    dict: "{" [pair ("," pair)*] "}"
    pair: string ":" disjunction

    STRING: /([ubf]?r?|r[ubf])("(?!"")[\s\S]*?(?<!\\)(\\\\)*?"|'(?!'')[\s\S]*?(?<!\\)(\\\\)*?')/i

    %import common.CNAME -> NAME
    %import common.INT
    %import common.FLOAT
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""


@v_args(inline=True)  # Affects the signatures of the methods
class OperatorTree(Transformer):
    from operator import (
        add,
        and_,
        eq,
        ge,
        getitem,
        gt,
        is_,
        is_not,
        le,
        lt,
        mod,
        mul,
        ne,
        neg,
        not_,
        or_,
        sub,
    )
    from operator import floordiv as floor
    from operator import truediv as div

    float = float
    integer = int
    slice = slice

    def __init__(self, vars: dict = {}):
        self.vars = vars

    def start(self, *args) -> str:
        if len(args) > 1:
            return "".join(args)
        if len(args) < 1:
            return ""
        return args[0]

    def string(self, s: str) -> str:
        return s[1:-1]

    def none(self) -> None:
        return None

    def true(self) -> bool:
        return True

    def false(self) -> bool:
        return False

    def list(self, *args) -> list:
        return list(args)

    def pair(self, key, value) -> tuple:
        return (key, value)

    def dict(self, *args) -> dict:
        return dict(args)

    def text(self, string) -> str:
        return str(string)

    def expression_wrapper(self, expression) -> Any:
        return expression

    def contains_(self, a: Any, b: Any) -> bool:
        return contains(b, a)

    def not_contains(self, a: Any, b: Any) -> bool:
        return not contains(b, a)

    def filter(self, a: Any, f: Any) -> Any:
        return f(a)

    def filter_func(self, name: Any, arguments: Any) -> Any:
        filters = FILTERS
        if name not in filters:
            raise KeyError(f"{name} is not a valid filter")
        f = filters[name]
        if arguments is not None:
            f = partial(f, *arguments)
        return f

    def arguments_wrapper(self, args) -> Any:
        return args

    def arguments(self, *args) -> Any:
        return list(args)

    def arg(self, a) -> Any:
        return a

    def var(self, name: str) -> Any:
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


_parser = Lark(_grammar, start="start", parser="lalr")


class Variable:
    def __init__(self, expression: Any):
        self.expression = expression
        self.parse_tree = None
        self.val = None
        self.has_var = None

        if isinstance(expression, str):
            self.parse_tree = self._compile(expression)
            self.has_var = self._find_var(self.parse_tree)

        if not self.has_var:
            transformer = OperatorTree({})
            self.val = transformer.transform(self.parse_tree)

    def _compile(self, expression: str) -> ParseTree:
        return _parser.parse(expression)

    def fetch(self, extend: dict = {}) -> Any:
        if self.parse_tree is None:
            return self.expression

        if not self.has_var:
            return self.val

        bb = ctx_blackboard.get()
        fd = ctx_flowdata.get()
        mcr = ctx_macros.get()
        vars = {"bb": bb, "fd": fd, "macro": mcr}
        vars.update(extend)
        transformer = OperatorTree(vars)
        result = transformer.transform(self.parse_tree)
        return result

    def _find_var(self, tree: Tree):
        for subtree in tree.iter_subtrees():
            if subtree.data == "var":
                return True
        return False
