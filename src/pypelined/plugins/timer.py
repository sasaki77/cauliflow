import asyncio
from datetime import datetime, timedelta

from pypelined.context import init_flowdata
from pypelined.node import TriggerNode, node


@node.register("interval")
class IntervalNode(TriggerNode):
    def set_argument_spec(self):
        return {
            "interval": {"type": "float", "required": True},
        }

    async def process(self) -> None:
        interval = self.params["interval"]
        last_time = datetime.now()

        while True:
            init_flowdata()
            await self.child.run()
            future_time = last_time + timedelta(seconds=interval)
            time_difference = (future_time - last_time).seconds
            if time_difference < 0:
                continue
            last_time = datetime.now()
            await asyncio.sleep(time_difference)
