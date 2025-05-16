import csv
from enum import StrEnum
from pathlib import Path

from pypelined.context import ctx_blackboard, ctx_flowdata
from pypelined.logging import get_logger
from pypelined.node import ArgumentSpec, ProcessNode, node

_logger = get_logger(__name__)


class DataFormat(StrEnum):
    ARRAY = "array"
    DICT = "dict"
    KEYVALUE = "key_value"


@node.register("input_csv")
class InputCSVNode(ProcessNode):
    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "path": {"type": "path", "required": True},
            "out_bb": {"type": "bool", "required": False, "default": False},
            "format": {"type": "str", "required": False, "default": "key_value"},
        }

    async def process(self) -> None:
        path = self.params["path"]
        format = self.params["format"]

        csvdata = self.get_csvdata(Path(path), format)

        outbb = self.params["out_bb"]
        if outbb:
            _bb = ctx_blackboard.get()
            _bb[self.name] = csvdata
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = csvdata

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
