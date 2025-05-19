import pytest
from cauliflow.context import ctx_blackboard, ctx_flowdata
from cauliflow.node import ArgumentSpec, Node


class NodeTest(Node):
    async def process(self) -> None:
        pass

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        self.set_common_output_args()
        return {
            "required_str": {"type": "str", "required": True},
            "not_required_str": {
                "type": "str",
                "required": False,
                "default": "default",
            },
            "not_required_bool": {
                "type": "bool",
                "required": False,
                "default": False,
            },
            "not_required_float": {
                "type": "float",
                "required": False,
                "default": 1.1,
            },
        }


class NodeTestWoDefault(Node):
    async def process(self) -> None:
        pass

    def set_argument_spec(self) -> dict[str, ArgumentSpec]:
        return {
            "wo_default": {"type": "str", "required": False},
        }


@pytest.mark.asyncio
async def test_node_with_positive_args():
    args = {
        "required_str": "foo",
        "not_required_str": "bar",
        "not_required_bool": True,
        "not_required_float": 2.2,
    }
    node = NodeTest(name="msg", param_dict=args)
    await node.run()
    assert node.params["required_str"] == "foo"
    assert node.params["not_required_str"] == "bar"
    assert node.params["not_required_bool"] is True
    assert node.params["not_required_float"] == 2.2


@pytest.mark.asyncio
async def test_node_without_default():
    args = {
        "required_str": "foo",
    }
    node = NodeTest(name="msg", param_dict=args)
    await node.run()
    assert node.params["required_str"] == "foo"
    assert node.params["not_required_str"] == "default"
    assert node.params["not_required_bool"] is False
    assert node.params["not_required_float"] == 1.1


@pytest.mark.asyncio
async def test_node_without_required():
    with pytest.raises(TypeError) as err:
        args = {}
        node = NodeTest(name="msg", param_dict=args)
        await node.run()
    assert "missing parameter required by" in str(err.value)


@pytest.mark.asyncio
async def test_node_wo_default():
    with pytest.raises(TypeError) as err:
        args = {}
        node = NodeTestWoDefault(name="msg", param_dict=args)
        await node.run()
    assert "default value is not specified" in str(err.value)


@pytest.mark.parametrize(
    "out_bb, out_field, ctx, expected_field",
    [
        (False, None, ctx_flowdata, "msg"),
        (False, "field", ctx_flowdata, "field"),
        (True, None, ctx_blackboard, "msg"),
        (True, "field", ctx_blackboard, "field"),
    ],
)
def test_output_bb(out_bb, out_field, ctx, expected_field, init_context_vars):
    args = {"required_str": "foo", "out_bb": out_bb, "out_field": out_field}
    node = NodeTest(name="msg", param_dict=args)
    node._fetch_params()
    node.output("test")
    dest = ctx.get()
    assert dest[expected_field] == "test"
