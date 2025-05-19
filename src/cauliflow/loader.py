from enum import StrEnum
from logging import getLogger
from pathlib import Path

import yaml
from cauliflow.context import ctx_macros
from cauliflow.flow import ConcurrentFlows, Flow, Flows, SequentialFlows
from cauliflow.macros import Macros

_logger = getLogger(__name__)


class FlowsType(StrEnum):
    SEQUENCTIAL = "sequential"
    CONCURRENT = "concurrent"


def flow_from_yaml(file_path: str | Path) -> Flows:
    yaml_dict = _load_yaml(file_path)

    is_seq = FlowsType.SEQUENCTIAL in yaml_dict
    is_con = FlowsType.CONCURRENT in yaml_dict
    is_onlyflow = "flow" in yaml_dict

    if (is_seq + is_con + is_onlyflow) > 1:
        _logger.error("multiple flows are detected")

    flows = None
    if is_seq:
        flows = _make_seq(yaml_dict[FlowsType.SEQUENCTIAL])
    elif is_con:
        flows = _make_con(yaml_dict[FlowsType.CONCURRENT])
    elif is_onlyflow:
        flow_dict = {"flows": [yaml_dict]}
        flows = _make_seq(flow_dict)
    else:
        _logger.error("flows not defined")
        raise TypeError

    if "macros" in yaml_dict:
        mcr = Macros()
        mcr.update(yaml_dict["macros"])
        ctx_macros.set(mcr)

    return flows


def _make_flows(flows: dict) -> list[Flows | Flow]:
    flow_list = []
    for flow in flows:
        new_flow = None
        if "flow" in flow:
            new_flow = _make_flow(flow)
        elif FlowsType.SEQUENCTIAL in flow:
            new_flow = _make_seq(flow[FlowsType.SEQUENCTIAL])
        elif FlowsType.CONCURRENT in flow:
            new_flow = _make_con(flow[FlowsType.CONCURRENT])
        else:
            continue
        flow_list.append(new_flow)
    return flow_list


def _make_seq(config: dict) -> Flows:
    if "flows" not in config:
        _logger.error("no flows in sequential flow")
    flows = SequentialFlows()
    flow_list = _make_flows(config["flows"])
    flows.extend(flow_list)
    return flows


def _make_con(config: dict) -> Flows:
    if "flows" not in config:
        _logger.error("no flows in concurrent flow")
    flows = ConcurrentFlows()
    flow_list = _make_flows(config["flows"])
    flows.extend(flow_list)
    return flows


def _make_flow(config: dict) -> Flow:
    if "flow" not in config:
        _logger.error("no flow in flow")
    name = config.get("name", None)
    flow = Flow(name=name)
    prev_node = "root"
    for node in config["flow"]:
        if len(node) != 1:
            _logger.error("node read error")
        for node_type, params in node.items():
            parent = prev_node
            name = node_type
            if "name" in params:
                name = params["name"]
                del params["name"]
            if "parent" in params:
                parent = params["parent"]
                del params["parent"]
            flow.create_node(node_type, _parent=parent, name=name, param_dict=params)
            prev_node = name
    return flow


def _load_yaml(file_path: str | Path) -> dict:
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data
