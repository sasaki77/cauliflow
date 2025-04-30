from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("message")
class MessageNode(ProcessNode):
    def __init__(self, _bb, name, msg):
        super().__init__(_bb, name)
        self.msg = Variable(msg, _bb)

    async def process(self, flowdata: FlowData):
        flowdata[self.name] = self.msg.fetch(flowdata)
        return flowdata
