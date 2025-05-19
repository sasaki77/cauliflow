import logging

from cauliflow.context import ctx_flow, ctx_node


class InjectingFilter(logging.Filter):
    def filter(self, record):
        flow = ctx_flow.get()
        node = ctx_node.get()
        record.flow_name = flow.name
        record.node_name = node.name
        return True


default_handler = logging.StreamHandler()
default_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(flow_name)s - %(node_name)s - %(message)s"
    )
)

default_handler.addFilter(InjectingFilter())


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.addHandler(default_handler)

    return logger
