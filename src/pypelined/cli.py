import asyncio
from logging import DEBUG, Formatter, StreamHandler, getLogger

import click

from pypelined.loader import flow_from_yaml
from pypelined.macros import Macros, macros
from pypelined.plugin_manager import PluginManager


def init_logger():
    logger = getLogger("pypelined")
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.propagate = False


@click.group()
def cli():
    pass


@cli.command()
@click.option("--macro", "-m", "_macros", type=(str, str), multiple=True)
@click.argument("filename", type=click.Path(exists=True))
def run(_macros, filename):
    init_logger()
    pm = PluginManager()
    pm.init()

    flows = flow_from_yaml(filename)

    macros_dict = dict(_macros)
    print(macros_dict)
    mcr = Macros()
    mcr.update(macros_dict)
    macros.set(mcr)
    asyncio.run(flows.run())


if __name__ == "__main__":
    cli()
