from pprint import pprint

from pypelined.flowdata import fd
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("stdout")
class OutNode(ProcessNode):
    def __init__(self, name, src=None, pretty=False):
        super().__init__(name)
        self.src = src if src is None else Variable(src)
        self.print_func = pprint if pretty else print

    async def process(self):
        flowdata = fd.get()
        if self.src is None:
            self.print_func(flowdata)
            return

        out = self.src.fetch(flowdata)
        self.print_func(out)
        return
