import asyncio
from datetime import datetime, timedelta

from cauliflow.context import init_flowdata
from cauliflow.node import ArgSpec, TriggerNode, node


@node.register("interval")
class IntervalNode(TriggerNode):
    """
    DOCUMENTATION:
      short_description: Run child node at a regular interval.
      description:
        - Run child node at a regular interval
      parameters:
        interval:
          description:
            - Interval to run child node in second.
    EXAMPLE: |-
      # Run child node every second
      - interval:
          name: "interval"
          interval: 1.0

      # Run child node. Interval is set by macro.
      - interval:
          name: "interval"
          interval: "{{ macro.interval }}"
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {"interval": ArgSpec(type="float", required=True)}

    async def process(self) -> None:
        interval = self.params["interval"]
        last_time = datetime.now()

        while True:
            init_flowdata()
            if self.child is not None:
                await self.child.run()
            future_time = last_time + timedelta(seconds=interval)
            time_difference = (future_time - last_time).seconds
            if time_difference < 0:
                continue
            last_time = datetime.now()
            await asyncio.sleep(time_difference)
