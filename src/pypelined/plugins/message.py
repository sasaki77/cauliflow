from pypelined.context import ctx_flowdata
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("message")
class MessageNode(ProcessNode):
    def __init__(self, name: str, msg: str):
        super().__init__(name)
        self.msg = Variable(msg)

    async def process(self) -> None:
        fd = ctx_flowdata.get()
        fd[self.name] = self.msg.fetch()
