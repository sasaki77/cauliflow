from pypelined.context import ctx_flowdata
from pypelined.node import ProcessNode, node


@node.register("message")
class MessageNode(ProcessNode):
    async def process(self) -> None:
        fd = ctx_flowdata.get()
        fd[self.name] = self.params["msg"]

    def set_argument_spec(self):
        return {
            "msg": {"type": "str", "required": True},
        }
