import asyncio
from logging import DEBUG, WARNING, getLogger

import click

from pypelined.context import ContextFlows, ctx_flows, ctx_macros
from pypelined.loader import flow_from_yaml
from pypelined.logging import get_logger
from pypelined.macros import Macros
from pypelined.plugin_manager import PluginManager

_logger = get_logger(__name__)


def init_logger(debug=False):
    logger = getLogger("pypelined")
    level = DEBUG if debug else WARNING
    logger.setLevel(level)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--macro", "-m", "macros", type=(str, str), multiple=True)
@click.option("--debug/--no-debug", default=False)
@click.argument("filename", type=click.Path(exists=True))
def run(macros, debug, filename):
    init_logger(debug)
    pm = PluginManager()
    pm.init()

    ctx_flows.set(ContextFlows(debug=debug))
    flows = flow_from_yaml(filename)

    macros_dict = dict(macros)
    mcr = Macros()
    mcr.update(macros_dict)
    ctx_macros.set(mcr)
    if debug:
        _logger.debug(f"macros={mcr}")
    asyncio.run(flows.run())


if __name__ == "__main__":
    cli()
