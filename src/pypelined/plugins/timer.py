import asyncio

from pypelined.flowdata import FlowData
from pypelined.node import TriggerNode, node
from pypelined.variable import Variable


@node.register("interval")
class IntervalNode(TriggerNode):
    def __init__(self, _bb, name, interval):
        super().__init__(_bb, name)
        self.interval = Variable(interval, _bb)

    async def process(self, flowdata: FlowData = None):
        interval = self.interval.fetch(flowdata)

        while True:
            await self.child.run()
            await asyncio.sleep(interval)
