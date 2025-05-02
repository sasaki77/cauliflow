from pprint import pprint

from pypelined.flowdata import flowdata
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable


@node.register("stdout")
class OutNode(ProcessNode):
    def __init__(self, name, src=None, pretty=False):
        super().__init__(name)
        self.src = src if src is None else Variable(src)
        self.print_func = pprint if pretty else print

    async def process(self):
        fd = flowdata.get()
        if self.src is None:
            self.print_func(fd)
            return

        out = self.src.fetch(fd)
        self.print_func(out)
        return
