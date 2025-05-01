import csv
import logging
from enum import StrEnum
from pathlib import Path

from pypelined.blackboard import bb
from pypelined.flowdata import fd
from pypelined.node import ProcessNode, node

_logger = logging.getLogger(__name__)


class DataFormat(StrEnum):
    ARRAY = "array"
    DICT = "dict"
    KEYVALUE = "key_value"


@node.register("input_csv")
class InputCSVNode(ProcessNode):
    def __init__(
        self,
        name,
        path: str,
        out_bb: bool = False,
        skip_header: bool = False,
        format: DataFormat = DataFormat.KEYVALUE,
    ):
        super().__init__(name)
        self.path = Path(path)
        self.out_bb = out_bb
        self.format = format

    async def process(self):
        csvdata = self.get_csvdata()
        _bb = bb.get()
        if self.out_bb:
            _bb[self.name] = csvdata
        else:
            flowdata = fd.get()
            flowdata[self.name] = csvdata

        return

    def get_csvdata(self):
        with self.path.open(newline="") as csvfile:
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
