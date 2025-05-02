from functools import singledispatch

import epics
import janus

from pypelined.context import ctx_flowdata, init_flowdata
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

    async def process(self):
        fd = ctx_flowdata.get()
        pvnames = self.pvnames.fetch(fd)
        pvnames = _get_pvnames(pvnames)

        for pvname in pvnames:
            pv = epics.get_pv(pvname, callback=self.onChanges)
            self.pvs.append(pv)

        while True:
            pvdata = await self.q.async_q.get()
            init_flowdata()
            d = ctx_flowdata.get()
            d[self.name] = pvdata
            await self.child.run()


@node.register("caget")
class CagetNode(ProcessNode):
    def __init__(self, name, pvname):
        super().__init__(name)
        self.pvnames = Variable(pvname)
        self.pvs: list[epics.PV] | epics.PV = None

    async def process(self):
        if self.pvs is None:
            pvnames = self.pvnames.fetch()
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
    print("str")
    return [string]
