import sys
from pathlib import Path

sys.path.append(str(Path("_ext").resolve()))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "cauliflow"
copyright = "2025, Shinya Sasaki"
author = "Shinya Sasaki"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "cauliflow_node",
    "cauliflow_filters",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_heading_anchors = 3

html_context = {
    "display_github": True,
    "github_user": "sasaki77",
    "github_repo": "cauliflow",
    "github_version": "master/docs/",
}

github_doc_root = "https://github.com/sasaki77/cauliflow/master/doc/"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = ["sphinx_rtd_theme.get_html_theme_path()"]

html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
