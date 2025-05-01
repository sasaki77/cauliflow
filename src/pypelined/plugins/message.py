from pypelined.flowdata import fd
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("message")
class MessageNode(ProcessNode):
    def __init__(self, name, msg):
        super().__init__(name)
        self.msg = Variable(msg)

    async def process(self):
        flowdata = fd.get()
        flowdata[self.name] = self.msg.fetch()
        return
