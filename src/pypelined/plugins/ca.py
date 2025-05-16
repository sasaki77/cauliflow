from functools import singledispatch

import epics
import janus

from pypelined.context import ctx_flowdata, init_flowdata
from pypelined.node import ArgumentSpec, ProcessNode, TriggerNode, node


@node.register("camonitor")
class CamonitorNode(TriggerNode):
    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        self.q = janus.Queue()
        self.pvs = []

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "pvname": {"type": "any", "required": True},
        }

    def onChanges(self, pvname=None, value=None, char_value=None, **kw):
        data = {"pv": {"name": pvname, "value": char_value}}
        self.q.sync_q.put(data)

    async def process(self):
        pvnames = self.params["pvname"]

        for pvname in pvnames:
            pv = epics.get_pv(pvname, callback=self.onChanges)
            self.pvs.append(pv)

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
    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        self.q = janus.Queue()
        self.pvs: list[epics.PV] | None = None

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "pvname": {"type": "any", "required": True},
        }

    async def process(self):
        if self.pvs is None:
            pvnames = self.params["pvname"]
            pvnames = _get_pvnames(pvnames)

            self.pvs = []
            for pvname in pvnames:
                pv = epics.get_pv(pvname)
                self.pvs.append(pv)

        out = []
        for pv in self.pvs:
            val = pv.get()
            out.append({"pvname": pv.pvname, "val": val})
        fd = ctx_flowdata.get()
        fd[self.name] = out
        return


@singledispatch
def _get_pvnames(obj):
    return obj


@_get_pvnames.register(str)
def _(string):
    return [string]
