from collections.abc import Callable

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from yaml import safe_load

from cauliflow.filters import FILTERS


class CauliFlowFilterDirective(SphinxDirective):
    has_content = False

    def run(self):
        section = nodes.section()
        section["ids"].append("filters")
        section += nodes.title(text="Filters")
        for name, func in FILTERS.items():
            sec = create_filter_sec(name, func)
            section += sec
        return [section]


def create_filter_sec(name: str, func: Callable) -> nodes.section:
    section = nodes.section()
    section["ids"].append(name)
    section += nodes.title(text=name)

    doc = None
    if func.__doc__ is not None:
        doc = safe_load(func.__doc__)

    if doc is None:
        return section

    desc = doc.get("description", None)

    if desc:
        for item_text in desc:
            para = nodes.paragraph(text=item_text)
            section += para

    params = create_params(doc)
    if params is not None:
        section += params

    example = create_example(doc)
    if example is not None:
        section += example

    return section


def create_params(doc: dict) -> nodes.definition_list | None:
    params = doc.get("parameters", None)
    if params is None:
        return None

    bullet_list = nodes.bullet_list()
    for name, info in params.items():
        para = nodes.paragraph()
        para += nodes.strong(text=name)
        para += nodes.Text(f" – {info['description']}")

        item = nodes.list_item()
        item += para
        bullet_list += item

    term = nodes.term(text="Parameters")
    item = nodes.definition_list_item("", term, bullet_list)

    definition_list = nodes.definition_list()
    definition_list += item

    return definition_list


def create_example(doc: dict) -> nodes.literal_block | None:
    example = doc.get("example", None)
    if example is None:
        return None

    text = example.strip()
    block = nodes.literal_block(text=text, language="yaml")
    return block


def setup(app):
    app.add_directive("cauliflow-filters", CauliFlowFilterDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
