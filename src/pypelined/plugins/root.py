from pypelined.flowdata import init_flowdata
from pypelined.node import ProcessNode, node


@node.register("root")
class RootNode(ProcessNode):
    async def process(self):
        init_flowdata()
        return
