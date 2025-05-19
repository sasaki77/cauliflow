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


@node.register("input_csv")
class InputCSVNode(ProcessNode):
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
