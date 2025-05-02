from operator import contains

from lark import Lark, Transformer, v_args

from pypelined.blackboard import blackboard
from pypelined.flowdata import flowdata
from pypelined.macros import macros

_grammar = """
    ?expression: disjunction
        | NAME "=" disjunction    -> assign_var

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

    def __init__(self, vars={}):
        self.vars = vars

    def string(self, s):
        return s[1:-1]

    def none(self):
        return None

    def true(self):
        return True

    def false(self):
        return False

    def list(self, *args):
        return list(args)

    def pair(self, key, value):
        return (key, value)

    def dict(self, *args):
        return dict(args)

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def contains_(self, a, b):
        return contains(b, a)

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


_parser = Lark(_grammar, start="expression", parser="lalr")


class Variable:
    def __init__(self, expression):
        self.expression = expression
        self.parse_tree = self.compile(expression)

    def compile(self, expression):
        return _parser.parse(expression)

    def fetch(self, extend: dict = {}):
        bb = blackboard.get()
        fd = flowdata.get()
        mcr = macros.get()
        vars = {"bb": bb, "fd": fd, "macros": mcr}
        vars.update(extend)
        transformer = OperatorTree(vars)
        result = transformer.transform(self.parse_tree)
        return result
