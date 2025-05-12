from operator import contains

from lark import Lark, ParseTree, Transformer, Tree, v_args

from pypelined.context import ctx_blackboard, ctx_flowdata, ctx_macros

_grammar = """
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

    ?atom_expr: atom
          | atom_expr "[" index "]"  -> getitem

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

    %import common.CNAME -> NAME
    %import common.INT
    %import common.FLOAT
    %import common.NUMBER
    %import common.WS_INLINE
    %import python.STRING

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
        mul,
        ne,
        neg,
        not_,
        or_,
        sub,
    )
    from operator import truediv as div

    float = float
    integer = int
    slice = slice

    def __init__(self, vars: dict = {}):
        self.vars = vars

    def start(self, *args) -> str:
        if len(args) > 1:
            return "".join(args)
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

    def expression_wrapper(self, expression) -> any:
        return expression

    def contains_(self, a: any, b: any) -> bool:
        return contains(b, a)

    def not_contains(self, a: any, b: any) -> bool:
        return not contains(b, a)

    def var(self, name: str) -> any:
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


_parser = Lark(_grammar, start="start", parser="lalr")


class Variable:
    def __init__(self, expression: any):
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

    def fetch(self, extend: dict = {}) -> any:
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
