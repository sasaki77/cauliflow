from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node


@node.register("root")
class RootNode(ProcessNode):
    async def process(self, flowdata: FlowData):
        return {}
