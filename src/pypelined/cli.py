from logging import DEBUG, Formatter, StreamHandler, getLogger

from pypelined.flow import Flow
from pypelined.flowdata import FlowData
from pypelined.node import ProcessNode, node
from pypelined.plugin_manager import PluginManager


@node.register("myout")
class MyOut(ProcessNode):
    async def process(self, flowdata: FlowData):
        print("hello")


def init_logger():
    logger = getLogger("pypelined")
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.propagate = False


def main() -> None:
    init_logger()
    pm = PluginManager()
    pm.init()

    flow = Flow()
    flow.create_node(
        "input_csv",
        _parent="root",
        name="csv",
        path="./test.csv",
        out_bb=True,
        format="key_value",
    )
    flow.create_node(
        "input_csv",
        _parent="csv",
        name="csv2",
        path="./test2.csv",
        out_bb=True,
        format="dict",
    )
    flow.create_node("message", _parent="csv2", name="msg", msg="['CALC', 'CALC2']")
    flow.create_node(
        "mutate",
        _parent="msg",
        name="mutate",
        target="bb['csv2']",
        out_bb=True,
        copy={"key_": "pvname"},
        split={"pvname": "."},
    )
    # flow.create_node("keys", _parent="csv", name="keys", input="bb['csv']", out_bb=True)
    # flow.create_node("interval", _parent="keys", name="interval", interval="1")
    # flow.create_node("camonitor", _parent="keys", name="ca", pvname="bb['keys']")
    # flow.create_node("caget", _parent="interval", name="ca", pvname="bb['keys']")
    # flow.create_node("camonitor", _parent="keys", name="ca", pvname="'TEST:CALC'")
    # flow.create_node(
    #    "concat",
    #    _parent="keys",
    #    name="ca",
    #    first="['Hello', 'こんにちわ']",
    #    second="[', World', '、 世界', 'unknown']",
    # )
    # flow.create_node("values", _parent=None, name="values", input="bb['csv']")
    # flow.create_node(
    #    "concat",
    #    _parent=None,
    #    name="concat",
    #    first="fd['forlist']",
    #    second="fd['values']",
    # )
    # flow.create_node(
    #    "for_list",
    #    _parent="msg",
    #    name="forlist",
    #    # forlist="[fd['msg'], bb['csv]]",
    #    # lists="[fd['msg'], ['TEST1', 'TEST2']]",
    #    # lists="[fd['msg'], bb['csv']]",
    #    # lists="[fd['msg'], {'TEST1': 'OK', 'TEST2': 'BB'}]",
    #    lists="{'TEST1': 'OK', 'TEST2': 'BB'}",
    #    # expression="item1_key + item0 + item1_val",
    #    expression="item0_key + item0_val",
    # )
    flow.create_node(
        "for_dict",
        _parent="mutate",
        name="forlist",
        # forlist="[fd['msg'], bb['csv]]",
        # lists="[fd['msg'], ['TEST1', 'TEST2']]",
        # lists="[fd['msg'], bb['csv']]",
        # lists="[fd['msg'], {'TEST1': 'OK', 'TEST2': 'BB'}]",
        lists="[bb['csv'], bb['mutate']]",
        # expression="item1_key + item0 + item1_item",
        key="item0_val + item1['pvname'][-1]",
        val="{'hostname': item0_key, 'item_key': item1['key_']}",
        filter="not 'zetemple' in item1['key_']",
    )
    flow.create_node("stdout", _parent="forlist", name="out", src="bb")
    flow.create_node("stdout", _parent="out", name="out2", src="fd")
    flow.create_node("myout", _parent="out2", name="myout")
    print(flow.nodes)
    flow.run()


if __name__ == "__main__":
    main()
