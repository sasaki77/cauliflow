import pytest

from cauliflow.plugins.file import OutFileNode


@pytest.mark.asyncio
async def test_output_file(init_context_vars, tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("test.txt")
    with open(fn, mode="w") as f:
        f.write("hello\n")

    node = OutFileNode(name="node", param_dict={"path": str(fn), "src": "hello"})
    await node.run()
    text = ""
    with open(fn) as f:
        text = f.read()
    assert text == "hello\nhello\n"

    await node.run()
    text = ""
    with open(fn) as f:
        text = f.read()
    assert text == "hello\nhello\nhello\n"
