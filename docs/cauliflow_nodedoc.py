from os import makedirs
from pathlib import Path

from cauliflow.node import FlowControlNode, NodeFactory, ProcessNode, TriggerNode
from cauliflow.plugin_manager import PluginManager


def main():
    pm = PluginManager()
    pm.init()

    registry = NodeFactory.registry
    dir = Path("nodes")

    makedirs(dir, exist_ok=True)
    for klass_dir in ["trigger", "process", "control"]:
        makedirs(dir / klass_dir, exist_ok=True)

    for name, klass in registry.items():
        if name == "root":
            continue

        klass_dir = None
        if issubclass(klass, TriggerNode):
            klass_dir = "trigger"
        elif issubclass(klass, ProcessNode):
            klass_dir = "process"
        elif issubclass(klass, FlowControlNode):
            klass_dir = "control"
        else:
            raise KeyError

        p = dir / klass_dir / f"{name}.rst"
        with open(p, mode="w") as f:
            f.write(f".. cauliflow-node:: {name}")


if __name__ == "__main__":
    main()
