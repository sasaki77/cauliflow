from contextvars import ContextVar
from dataclasses import dataclass

from pypelined.blackboard import BlackBoard
from pypelined.flowdata import FlowData
from pypelined.macros import Macros


@dataclass
class ContextFlows:
    debug: bool = False


@dataclass
class ContextFlow:
    name: str = None


@dataclass
class ContextNode:
    name: str = None


ctx_macros = ContextVar("pypelined.ctx_macros", default=Macros())
ctx_flowdata = ContextVar("pypelined.ctx_flowdata", default=FlowData())
ctx_blackboard = ContextVar("pypelined.ctx_blackboard", default=BlackBoard())
ctx_flows = ContextVar("pypelind.ctx_flows", default=ContextFlows())
ctx_flow = ContextVar("pypelind.ctx_flow", default=ContextFlow())
ctx_node = ContextVar("pypelind.ctx_node", default=ContextNode())


def init_flowdata():
    ctx_flowdata.set(FlowData())
