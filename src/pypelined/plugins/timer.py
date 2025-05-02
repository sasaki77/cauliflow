import asyncio

from pypelined.context import init_flowdata
from pypelined.node import TriggerNode, node
from pypelined.variable import Variable


@node.register("interval")
class IntervalNode(TriggerNode):
    def __init__(self, name, interval):
        super().__init__(name)
        self.interval = Variable(interval)

    async def process(self):
        interval = self.interval.fetch()

        while True:
            init_flowdata()
            await self.child.run()
            await asyncio.sleep(interval)
