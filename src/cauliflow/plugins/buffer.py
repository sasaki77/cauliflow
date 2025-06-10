import asyncio

from cauliflow.context import ctx_flowdata
from cauliflow.flowdata import FlowData
from cauliflow.node import ArgSpec, FlowControlNode, node


@node.register("buffer")
class BufferNode(FlowControlNode):
    """
    DOCUMENTATION:
      short_description: Buffering input data.
      description:
          - Buffering input data.
          - The child nodes are processed either when the data exceeds the buffer size or after a certain amount of time has passed. At that point, the buffer data is written to the FlowData.
      parameters:
        size:
          description:
            - Buffer size.
        timeout:
          description:
            - The waiting period for new data to arrive.
            - If this period expires, the child nodes are processed.
            - If the input data exceeds the buffer size, the child nodes are processed immediately.
        input:
          description:
            - Input data to be buffered.
        flatten:
          description:
            - When flatten is True, the input list is flattened before being stored in the buffer.
    EXAMPLE: |-
      # Buffer for scalar data
      - buffer:
          name: "buffer"
          size: 10
          timeout: 5
          input: "{{ fd.input }}"

      # Buffer for list data with flatten
      - buffer:
          name: "buffer"
          size: 10
          timeout: 5
          input: "{{ fd.input }}"
          flatten: yes
    """

    def __init__(self, name: str, param_dict: dict | None = None):
        super().__init__(name, param_dict)
        self.buffer = []
        self.lock = asyncio.Lock()
        self.timer_task = None

    # redeclare run not to run a child node
    async def run(self) -> None:
        await self._run_self()

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "size": ArgSpec(type="int", required=False, default=50),
            "timeout": ArgSpec(type="float", required=False, default=5.0),
            "input": ArgSpec(type="Any", required=True),
            "flatten": ArgSpec(type="bool", required=False, default=False),
        }

    async def process(self) -> None:
        input = self.params["input"]
        size = self.params["size"]
        timeout = self.params["timeout"]
        flatten = self.params["flatten"]

        async with self.lock:
            if flatten:
                self.buffer.extend(input)
            else:
                self.buffer.append(input)

            if len(self.buffer) >= size:
                await self.flush()
            elif self.timer_task is None:
                self.timer_task = asyncio.create_task(self.start_timer(timeout))

    async def start_timer(self, timeout):
        await asyncio.sleep(timeout)
        async with self.lock:
            if self.buffer:
                await self.flush()

    async def flush(self):
        if self.buffer:
            # buffer node resets the flowdata with buffer data
            flowdata = {self.name: self.buffer}
            ctx_flowdata.set(FlowData(flowdata))
            self.buffer = []

            if self.timer_task:
                self.timer_task.cancel()
            self.timer_task = None

            await self._run_child()
