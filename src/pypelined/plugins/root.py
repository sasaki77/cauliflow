from pypelined.context import init_flowdata
from pypelined.node import ProcessNode, node


@node.register("root")
class RootNode(ProcessNode):
    async def process(self) -> None:
        init_flowdata()
