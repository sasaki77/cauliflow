from contextvars import ContextVar
from dataclasses import dataclass

from cauliflow.blackboard import BlackBoard
from cauliflow.flowdata import FlowData
from cauliflow.macros import Macros


@dataclass
class ContextFlows:
    debug: bool = False


@dataclass
class ContextFlow:
    name: str | None = None


@dataclass
class ContextNode:
    name: str | None = None


ctx_macros = ContextVar("cauliflow.ctx_macros", default=Macros())
ctx_flowdata = ContextVar("cauliflow.ctx_flowdata", default=FlowData())
ctx_blackboard = ContextVar("cauliflow.ctx_blackboard", default=BlackBoard())
ctx_flows = ContextVar("pypelind.ctx_flows", default=ContextFlows())
ctx_flow = ContextVar("pypelind.ctx_flow", default=ContextFlow())
ctx_node = ContextVar("pypelind.ctx_node", default=ContextNode())


def init_flowdata() -> None:
    ctx_flowdata.set(FlowData())
