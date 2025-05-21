from os import makedirs
from pathlib import Path

from cauliflow.node import NodeFactory
from cauliflow.plugin_manager import PluginManager


def main():
    pm = PluginManager()
    pm.init()

    registry = NodeFactory.registry
    dir = Path("nodes")
    makedirs(dir, exist_ok=True)
    for name, klass in registry.items():
        if name == "root":
            continue
        p = dir / f"{name}.rst"
        with open(p, mode="w") as f:
            f.write(f".. cauliflow-node:: {name}")


if __name__ == "__main__":
    main()
