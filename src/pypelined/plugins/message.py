from pypelined.node import ArgumentSpec, ProcessNode, node


@node.register("message")
class MessageNode(ProcessNode):
    async def process(self) -> None:
        self.output(self.params["msg"])

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        self.set_common_output_args()
        return {
            "msg": {"type": "str", "required": True},
        }
