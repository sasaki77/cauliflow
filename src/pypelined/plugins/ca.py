from functools import singledispatch

import epics
import janus

from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, TriggerNode, node
from pypelined.variable import Variable


@node.register("camonitor")
class CamonitorNode(TriggerNode):
    def __init__(self, name, pvname):
        super().__init__(name)
        self.q = janus.Queue()
        self.pvnames = Variable(pvname)
        self.pvs = []

    def onChanges(self, pvname=None, value=None, char_value=None, **kw):
        data = {"pv": {"name": pvname, "value": char_value}}
        self.q.sync_q.put(data)

    async def process(self, flowdata: FlowData = None):
        pvnames = self.pvnames.fetch(flowdata)
        pvnames = _get_pvnames(pvnames)

        for pvname in pvnames:
            pv = epics.get_pv(pvname, callback=self.onChanges)
            self.pvs.append(pv)

        while True:
            pvdata = await self.q.async_q.get()
            d = FlowData()
            d = {self.name: pvdata}
            await self.child.run(d)


@node.register("caget")
class CagetNode(ProcessNode):
    def __init__(self, name, pvname):
        super().__init__(name)
        self.pvnames = Variable(pvname)
        self.pvs: list[epics.PV] | epics.PV = None

    async def process(self, flowdata: FlowData):
        if self.pvs is None:
            pvnames = self.pvnames.fetch(flowdata)
            pvnames = _get_pvnames(pvnames)

            self.pvs = []
            for pvname in pvnames:
                pv = epics.get_pv(pvname)
                self.pvs.append(pv)

        out = []
        for pv in self.pvs:
            val = pv.get()
            out.append({"pvname": pv.pvname, "val": val})
        flowdata[self.name] = out
        return flowdata


@singledispatch
def _get_pvnames(obj):
    return obj


@_get_pvnames.register(str)
def _(string):
    print("str")
    return [string]
