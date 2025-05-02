from contextvars import ContextVar

from pypelined.blackboard import BlackBoard
from pypelined.flowdata import FlowData
from pypelined.macros import Macros

ctx_macros = ContextVar("pypelined.ctx_macros", default=Macros())
ctx_flowdata = ContextVar("pypelined.ctx_flowdata", default=FlowData())
ctx_blackboard = ContextVar("pypelined.ctx_blackboard", default=BlackBoard())


def init_flowdata():
    ctx_flowdata.set(FlowData())
