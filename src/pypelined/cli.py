import asyncio
from logging import DEBUG, getLogger

import click

from pypelined.context import ctx_macros
from pypelined.loader import flow_from_yaml
from pypelined.macros import Macros
from pypelined.plugin_manager import PluginManager


def init_logger():
    logger = getLogger("pypelined")
    logger.setLevel(DEBUG)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--macro", "-m", "macros", type=(str, str), multiple=True)
@click.argument("filename", type=click.Path(exists=True))
def run(macros, filename):
    init_logger()
    pm = PluginManager()
    pm.init()

    flows = flow_from_yaml(filename)

    macros_dict = dict(macros)
    print(macros_dict)
    mcr = Macros()
    mcr.update(macros_dict)
    ctx_macros.set(mcr)
    asyncio.run(flows.run())


if __name__ == "__main__":
    cli()
