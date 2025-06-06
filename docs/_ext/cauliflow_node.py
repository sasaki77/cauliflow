from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from yaml import safe_load

from cauliflow.node import ArgSpec, NodeFactory
from cauliflow.plugin_manager import PluginManager


class CauliFlowNodeDirective(SphinxDirective):
    required_arguments = 1
    has_content = False

    def run(self):
        node_type = self.arguments[0]
        node = NodeFactory.get(node_type)

        doc_src = None
        if node.__doc__ is not None:
            doc_src = safe_load(node.__doc__)

        doc_data = doc_src.get("DOCUMENTATION", None) if doc_src else None
        parameters = {}
        if doc_data:
            parameters = doc_data["parameters"] if "parameters" in doc_data else {}

        example = doc_src.get("EXAMPLE", None) if doc_src else None

        section = nodes.section()
        section["ids"].append(node_type)
        section += nodes.title(text=node_type)

        desc_txt = ""
        if doc_data is not None:
            desc_txt = doc_data.get("short_description", "No description")
        desc_param = nodes.paragraph(text=desc_txt)
        section += desc_param

        instance = node("instance")  # type: ignore
        instance.set_argument_spec()

        desc = doc_data.get("description", None) if doc_data is not None else None
        section += create_desc_section(desc)
        section += create_param_section(instance.argument_spec, parameters)
        section += create_examples_section(example)

        return [section]


def create_desc_section(desc: list[str] | None) -> nodes.section:
    section = nodes.section()
    section["ids"].append("description")
    section += nodes.title(text="Description")

    if desc is None:
        return section

    desc_bullet = nodes.bullet_list()
    for item_text in desc:
        item = nodes.list_item()
        para = nodes.paragraph(text=item_text)
        item += para
        desc_bullet += item

    section += desc_bullet

    return section


def create_param_section(args: dict[str, ArgSpec], doc_param: dict) -> nodes.section:
    colums = ["Parameter", "Type", "Required", "Default", "Comment"]
    no_colums = len(colums)

    # Table
    table = nodes.table()

    # Table group
    tgroup = nodes.tgroup(cols=no_colums)
    table += tgroup

    for _ in range(no_colums):
        tgroup += nodes.colspec(colwidth=1)

    # Header
    thead = nodes.thead()
    tgroup += thead

    header_row = nodes.row()
    for text in colums:
        entry = nodes.entry()
        entry += nodes.paragraph(text=text)
        header_row += entry
    thead += header_row

    # Body
    tbody = nodes.tbody()
    tgroup += tbody

    for name, data in sorted(args.items()):
        row = nodes.row()

        name_entry = nodes.entry()
        type_entry = nodes.entry()
        required_entry = nodes.entry()
        default_entry = nodes.entry()
        comment_entry = nodes.entry()

        required_txt = "Yes" if data.required else "No"
        default_txt = "-" if data.required else data.default
        comment_txt_list = (
            doc_param[name].get("description", "") if name in doc_param else ""
        )

        # name_entry += nodes.paragraph(text=str(name))
        name_entry += nodes.paragraph()
        name_entry += nodes.strong(text=str(name))
        type_entry += nodes.paragraph(text=data.type)
        required_entry += nodes.paragraph(text=str(required_txt))
        default_entry += nodes.paragraph(text=str(default_txt))
        for line in comment_txt_list:
            comment_entry += nodes.paragraph(text=line)

        row += name_entry
        row += type_entry
        row += required_entry
        row += default_entry
        row += comment_entry
        tbody += row

    section = nodes.section()
    section["ids"].append("parameters")
    section += nodes.title(text="Parameters")
    section += table

    return section


def create_examples_section(examples: str | None) -> nodes.section:
    section = nodes.section()
    section["ids"].append("examples")
    section += nodes.title(text="Examples")
    text = examples.strip() if examples else "No Examples"
    section += nodes.literal_block(text=text, language="yaml")
    return section


def setup(app):
    pm = PluginManager()
    pm.init()

    app.add_directive("cauliflow-node", CauliFlowNodeDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
