from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("message")
class MessageNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Output data to flowdata or blackboard.
      description:
          - This node outputs data to flowdata or blackboard
      parameters:
        msg:
          description:
          - Output data.
    EXAMPLE: |-
      # Output "hello" to the flowdata["msg"]
      - message:
          name: "msg"
          msg: "hello"

      # Output the value of 'foo' field in the blackboard to the flowdata["msg"]
      - message:
          name: "msg"
          msg: "{{ bb.foo }}"

      # Output "hello" to the flowdata["field"]
      - message:
          name: "msg"
          msg: "hello"
          out_field: "field"

      # Output "hello" to the blackboard["msg"]
      - message:
          name: "msg"
          msg: "hello"
          out_bb: yes
    """

    async def process(self) -> None:
        self.output(self.params["msg"])

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {"msg": ArgSpec(type="any", required=True)}
