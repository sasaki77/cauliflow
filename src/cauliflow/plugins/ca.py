from functools import singledispatch
from typing import cast

import janus
from aioca import CANothing, caget, camonitor, caput

from cauliflow.context import ctx_flowdata, init_flowdata
from cauliflow.node import ArgSpec, ProcessNode, TriggerNode, node


@node.register("camonitor")
class CamonitorNode(TriggerNode):
    """
    DOCUMENTATION:
      short_description: Monitor EPICS PV(s) and pass it flowdata.
      description:
        - Monitor EPICS PV(s) and pass it flowdata.
      parameters:
        pvname:
          description:
            - A pvname or a list of pvname.
    EXAMPLE: |-
      # Monitor single pv data.
      # Output: {'name': 'TEST:PV1', 'value': 7.0, 'timestamp': 1749196716.822903, 'status': 0, 'severity': 0, 'ok': True}
      - camonitor:
          pvname: "TEST:PV1"

      # Monitor list of pv data.
      # Output: {'name': 'TEST:PV1', 'value': 7.0, 'timestamp': 1749196716.822903, 'status': 0, 'severity': 0, 'ok': True}
      - camonitor:
          pvname: ["TEST:PV1", "TEST:PV2"]
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.q = janus.Queue()
        self.pvs = []

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "pvname": ArgSpec(type="any", required=True),
        }

    def callback(self, val, _):
        if val.ok:
            data = {
                "name": val.name,
                "value": val,
                "timestamp": val.timestamp,
                "status": val.status,
                "severity": val.severity,
                "ok": True,
            }
        else:
            data = {"name": val.name, "ok": False}

        self.q.sync_q.put(data)

    async def process(self):
        pvnames = self.params["pvname"]
        pvnames = _get_pvnames(pvnames)

        camonitor(
            pvnames, self.callback, format=1, all_updates=True, notify_disconnect=True
        )

        while True:
            pvdata = await self.q.async_q.get()
            init_flowdata()
            d = ctx_flowdata.get()
            d[self.name] = pvdata
            if self.child is None:
                continue
            await self.child.run()


@node.register("caget")
class CagetNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Get EPICS PV(s) and pass it flowdata.
      description:
        - Get EPICS PV(s) and pass it flowdata.
      parameters:
        pvname:
          description:
            - A pvname or a list of pvname.
        timeout:
          description:
            - Wait time.
    EXAMPLE: |-
      # Get single pv data.
      # Output: {'name': 'TEST:PV1', 'value': 7.0, 'timestamp': 1749196716.822903, 'status': 0, 'severity': 0, 'ok': True}
      - caget:
          pvname: "TEST:PV1"

      # Get list of pv data.
      # Output: [
      #  {'name': 'TEST:PV1', 'value': 7.0, 'timestamp': 1749196716.822903, 'status': 0, 'severity': 0, 'ok': True},
      #  {'name': 'TEST:PV2', 'value': 8.0, 'timestamp': 1749196717.822903, 'status': 0, 'severity': 0, 'ok': True},
      # ]
      - caget:
          pvname: ["TEST:PV1", "TEST:PV2"]

      # Get single pv data with timeout.
      # Timeout Output: {'name': 'TEST:PV1', 'ok': False}
      - caget:
          pvname: "TEST:PV1"
          timeout: 1.0
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "pvname": ArgSpec(type="str|list[str]", required=True),
            "timeout": ArgSpec(type="float", required=False, default=5.0),
        }

    async def process(self):
        pvnames = self.params["pvname"]
        is_single = isinstance(pvnames, str)
        pvnames = _get_pvnames(pvnames)

        vals = await caget(
            pvnames, format=1, timeout=self.params["timeout"], throw=False
        )

        out = []
        for val in vals:
            if val.ok:
                data = {
                    "name": val.name,
                    "value": val,
                    "timestamp": val.timestamp,
                    "status": val.status,
                    "severity": val.severity,
                    "ok": True,
                }
            else:
                data = {"name": val.name, "ok": False}
            out.append(data)

        if is_single:
            out = out[0]

        fd = ctx_flowdata.get()
        fd[self.name] = out


@node.register("caput")
class CaputNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Put values to EPICS PV(s).
      description:
        - Put values to EPICS PV(s).
      parameters:
        pvname:
          description:
            - A pvname or a list of pvname.
        value:
          description:
            - A value or a list of value.
        repeat_value:
          description:
            - Put the same value to every PV if True.
        timeout:
          description:
            - Wait time.
    EXAMPLE: |-
      # Put to a single PV.
      # Output: {'name': 'TEST:PV1', 'ok': True}
      - caput:
          pvname: "TEST:PV1"
          value: 1.0

      # Put 1 to TEST:PV1 and 2 to TEST:PV2.
      # Output: [
      #  {'name': 'TEST:PV1', 'ok': True}
      #  {'name': 'TEST:PV2', 'ok': True}
      # ]
      - caput:
          pvname: ["TEST:PV1", "TEST:PV2"]
          value: [1.0, 2.0]

      # Put 1 to TEST:PV1 and TEST:PV2 with repeat_value.
      # Output: [
      #  {'name': 'TEST:PV1', 'ok': True}
      #  {'name': 'TEST:PV2', 'ok': True}
      # ]
      - caput:
          pvname: ["TEST:PV1", "TEST:PV2"]
          value: 1.0
          repeat_value: yes

      # Put to a single pv data with timeout.
      # Timeout Output: {'name': 'TEST:PV1', 'ok': False}
      - caput:
          pvname: "TEST:PV1"
          value: 1.0
          timeout: 1.0
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "pvname": ArgSpec(type="str|list[str]", required=True),
            "value": ArgSpec(type="Any|list[Any]", required=True),
            "repeat_value": ArgSpec(type="bool", required=False),
            "timeout": ArgSpec(type="float", required=False, default=5.0),
        }

    async def process(self):
        pvnames = self.params["pvname"]
        is_single = isinstance(pvnames, str)

        vals = None
        if is_single:
            vals = await caput(
                pvnames,
                self.params["value"],
                wait=True,
                timeout=self.params["timeout"],
                throw=False,
            )
        else:
            vals = await caput(
                pvnames,
                self.params["value"],
                repeat_value=self.params["repeat_value"],
                wait=True,
                timeout=self.params["timeout"],
                throw=False,
            )

        out = None
        if is_single:
            vals = cast(CANothing, vals)
            out = {"name": vals.name, "ok": vals.ok}
        else:
            vals = cast(list[CANothing], vals)
            out = [{"name": val.name, "ok": val.ok} for val in vals]

        fd = ctx_flowdata.get()
        fd[self.name] = out


@singledispatch
def _get_pvnames(obj):
    return obj


@_get_pvnames.register(str)
def _(string):
    return [string]
