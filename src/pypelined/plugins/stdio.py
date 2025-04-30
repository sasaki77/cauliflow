from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("stdout")
class OutNode(ProcessNode):
    def __init__(self, _bb, name, src=None):
        super().__init__(_bb, name)
        self.src = src if src is None else Variable(src, _bb)

    async def process(self, flowdata: FlowData):
        if self.src is None:
            print(flowdata)
            return flowdata

        out = self.src.fetch(flowdata)
        print(out)
        return flowdata
