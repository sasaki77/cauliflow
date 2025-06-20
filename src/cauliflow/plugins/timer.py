import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

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


@node.register("scheduler")
class Scheduler(TriggerNode):
    """
    DOCUMENTATION:
      short_description: Run child node at a regular interval or cron schedule.
      description:
        - Run child node at a regular interval or cron schedule.
        - If a value is set for both interval and cron, interval takes precedence.
      parameters:
        interval:
          description:
            - Interval to run child node in second.
        cron:
          description:
            - Specify schedule in cron style.
    EXAMPLE: |-
      # Run child node every second
      - scheduler:
          name: "scheduler"
          interval: 1.0

      # Run child node. Interval is set by macro.
      - scheduler:
          name: "scheduler"
          interval: "{{ macro.interval }}"

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
            "interval": ArgSpec(type="float", required=False, default=None),
            "cron": ArgSpec(type="str", required=False, default=None),
        }

    async def process(self) -> None:
        interval = self.params["interval"]
        cron = self.params["cron"]

        if interval is None and cron is None:
            raise ValueError(
                "interval and cron are None. Either one of them must be set to a value."
            )

        if interval:
            trigger = IntervalTrigger(seconds=interval)
        else:
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
