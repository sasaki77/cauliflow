import asyncio
from time import monotonic

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
        next_time = monotonic()

        while True:
            init_flowdata()
            if self.child is not None:
                await self.child.run()
            next_time += interval
            sleep_duration = max(0, next_time - monotonic())
            await asyncio.sleep(sleep_duration)


@node.register("scheduler")
class Scheduler(TriggerNode):
    """
    DOCUMENTATION:
      short_description: Run child node at a cron schedule.
      description:
        - Run child node at a cron schedule.
      parameters:
        cron:
          description:
            - Specify schedule in cron style.
    EXAMPLE: |-
      # Run child node every minute
      - scheduler:
          name: "scheduler"
          cron: "*/1 * * * *"

      # Run child node every day at 12:30
      - scheduler:
          name: "scheduler"
          cron: "30 12 * * *"
    """

    _scheduler = AsyncIOScheduler()

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "cron": ArgSpec(type="str", required=True),
        }

    async def process(self) -> None:
        cron = self.params["cron"]

        cron_args = _parse_cron_string(cron)
        trigger = CronTrigger(**cron_args)
        self._scheduler.add_job(self._job, trigger)

        if not self._scheduler.running:
            self._scheduler.start()

        while True:
            await asyncio.sleep(1)

    async def _job(self):
        init_flowdata()
        if self.child is not None:
            await self.child.run()


def _parse_cron_string(cron_string: str):
    parts = cron_string.split()
    if len(parts) != 5:
        raise ValueError(
            "Invalid cron string format. Expected format: 'minute hour day month day_of_week'"
        )

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }
