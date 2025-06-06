from pathlib import Path

import aiofiles

from cauliflow.node import ArgSpec, ProcessNode, node


@node.register("out_file")
class OutFileNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Output the data to the file.
      description:
        - Output the data to the file.
      parameters:
        path:
          description:
            - The path to the file to output.
        src:
          description:
            - Data to output.
    EXAMPLE: |-
      # Output hello to test.txt
      - out_file:
          name: "out"
          path: "./test.txt"
          src: "hello"

      # Output csv data in blackboard to test.txt
      - out_file:
          name: "out"
          path: "./test.txt"
          src: "{{ bb.csv }}"
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "path": ArgSpec(type="path", required=True),
            "src": ArgSpec(type="str", required=True),
        }

    async def process(self) -> None:
        path = Path(self.params["path"])
        src = self.params["src"]
        async with aiofiles.open(path, mode="a") as f:
            await f.write(src + "\n")
