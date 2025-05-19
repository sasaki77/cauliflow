from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("message")
class MessageNode(ProcessNode):
    async def process(self) -> None:
        self.output(self.params["msg"])

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {"msg": ArgSpec(type="str", required=True)}
