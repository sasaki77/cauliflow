import csv
from enum import StrEnum
from pathlib import Path

from cauliflow.logging import get_logger
from cauliflow.node import ArgSpec, ProcessNode, node

_logger = get_logger(__name__)


class DataFormat(StrEnum):
    ARRAY = "array"
    DICT = "dict"
    KEYVALUE = "key_value"


@node.register("in_csv")
class InputCSVNode(ProcessNode):
    """
    DOCUMENTATION:
      short_description: Read csv file and output the data to flowdata or blackboard.
      description:
        - Read csv file and output the data to flowdata or blackboard.
        - Output format can be chosen array, dict or key_value.
      parameters:
        path:
          description:
            - The path to the csv file to read.
        format:
          description:
            - Output format.
            - Choose array, dict or key_value.
    EXAMPLE: |-
      # Assume following csv file is located at "./file.csv"
      # id, name
      # foo, John
      # bar, Tom

      # Read the csv file as key_value and output it to blackboard
      # Output: {"csv": {'foo': 'John', 'bar': 'Tom'}}
      - in_csv:
          name: "csv"
          path: "./file.csv"
          format: "key_value"
          out_bb: yes

      # Read the csv file as dict
      # Output: {"csv": [{'id': 'foo', 'name': 'John'}, {'id': 'bar', 'name': 'Tom'}]}
      - in_csv:
          name: "csv"
          path: "./file.csv"
          format: "dict"

      # Read the csv file as dict
      # Output: {"csv": [["id", "name"], ["foo", "John"], ["bar", "Tom"]]}
      - in_csv:
          name: "csv"
          path: "./file.csv"
          format: "array"
    """

    def set_argument_spec(self) -> dict[str, ArgSpec]:
        self.set_common_output_args()
        return {
            "path": ArgSpec(type="path", required=True),
            "format": ArgSpec(type="str", required=False, default="key_value"),
        }

    async def process(self) -> None:
        path = self.params["path"]
        format = self.params["format"]

        csvdata = self.get_csvdata(Path(path), format)
        self.output(csvdata)

    def get_csvdata(self, path: Path, format: str | DataFormat) -> dict | list | None:
        with path.open(newline="") as csvfile:
            if format == DataFormat.DICT:
                reader = csv.DictReader(csvfile, skipinitialspace=True)
                dictlist = [row for row in reader]
                return dictlist

            reader = csv.reader(csvfile, skipinitialspace=True)
            if format == DataFormat.ARRAY:
                csvdata = [row for row in reader]
                return csvdata

            if format == DataFormat.KEYVALUE:
                csvdata = {}
                for row in reader:
                    csvdata[row[0]] = row[1]
                return csvdata

            _logger.warning(f"format:{format} is not matched")
