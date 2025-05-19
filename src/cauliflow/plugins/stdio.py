from pprint import pprint

from cauliflow.context import ctx_flowdata
from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("stdout")
class OutNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgSpec]:
        return {
            "src": ArgSpec(type="any", required=False, default=None),
            "pretty": ArgSpec(type="bool", required=False, default=False),
        }

    async def process(self) -> None:
        print_func = pprint if self.params["pretty"] else print
        src = self.params["src"]

        if src is None:
            fd = ctx_flowdata.get()
            print_func(fd)
            return

        print_func(src)
