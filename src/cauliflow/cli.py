import asyncio
from logging import DEBUG, WARNING, getLogger

import click
from cauliflow.context import ContextFlows, ctx_flows, ctx_macros
from cauliflow.loader import flow_from_yaml
from cauliflow.logging import get_logger
from cauliflow.plugin_manager import PluginManager

_logger = get_logger(__name__)


def init_logger(debug: bool = False) -> None:
    logger = getLogger("cauliflow")
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
    mcr = ctx_macros.get()
    mcr.update(macros_dict)
    ctx_macros.set(mcr)
    if debug:
        _logger.debug(f"macros={mcr}")
    asyncio.run(flows.run())


if __name__ == "__main__":
    cli()
