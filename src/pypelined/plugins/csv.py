import csv
from enum import StrEnum
from pathlib import Path

from pypelined.context import ctx_blackboard, ctx_flowdata
from pypelined.logging import get_logger
from pypelined.node import ProcessNode, node
from pypelined.variable import Variable

_logger = get_logger(__name__)


class DataFormat(StrEnum):
    ARRAY = "array"
    DICT = "dict"
    KEYVALUE = "key_value"


@node.register("input_csv")
class InputCSVNode(ProcessNode):
    def __init__(
        self,
        name: str,
        path: str,
        out_bb: bool = False,
        skip_header: bool = False,
        format: str | DataFormat = DataFormat.KEYVALUE,
    ):
        super().__init__(name)
        self.path = Variable(path)
        self.out_bb = out_bb
        self.format = format

    async def process(self) -> None:
        path = self.path.fetch()
        csvdata = self.get_csvdata(Path(path))
        _bb = ctx_blackboard.get()
        if self.out_bb:
            _bb[self.name] = csvdata
        else:
            fd = ctx_flowdata.get()
            fd[self.name] = csvdata

    def get_csvdata(self, path: Path) -> None:
        with path.open(newline="") as csvfile:
            if self.format == DataFormat.DICT:
                reader = csv.DictReader(csvfile, skipinitialspace=True)
                dictlist = [row for row in reader]
                return dictlist

            reader = csv.reader(csvfile, skipinitialspace=True)
            if self.format == DataFormat.ARRAY:
                csvdata = [row for row in reader]
                return csvdata

            if self.format == DataFormat.KEYVALUE:
                csvdata = {}
                for row in reader:
                    csvdata[row[0]] = row[1]
                return csvdata

            _logger.warning(f"format:{self.format} is not matched")
