from pprint import pprint

from cauliflow.context import ctx_flowdata
from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("stdout")
class OutNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Print data to stdout.
      description:
        - stdout node prints the data to the standart output
      parameters:
        src:
          description:
            - Data to print.
            - If src is not set, the stdout node prints the flowdata.
        pretty:
          description:
            - Enable pretty print.

    EXAMPLE: |-
      # Print flowdata to stdout
      - stdout:
          name: "stdout"

      # Print "hello" to stdout
      - stdout:
          name: "stdout"
          src: "hello"

      # Pretty print the value of 'foo' field in the blackboard to stdout
      - stdout:
          name: "stdout"
          src: "{{ bb.foo }}"
          pretty: yes
    """

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
