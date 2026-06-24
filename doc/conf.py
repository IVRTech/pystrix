# -*- coding: utf-8 -*-
import os
import re
import sys

sys.path.append(os.path.abspath(".."))
import pystrix as module

sys.path.remove(os.path.abspath(".."))
sys.path.append(os.path.abspath("../pystrix"))

extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo", "sphinx.ext.coverage"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = "pystrix"
copyright = module.COPYRIGHT
version = re.match(r"^(\d+\.\d+)", module.VERSION).group(1)
release = module.VERSION

exclude_patterns = ["_build"]

pygments_style = "sphinx"

# Prefer the Read the Docs theme when it is installed; fall back to the
# bundled 'alabaster' theme so local builds work without extra packages.
try:
    import sphinx_rtd_theme  # noqa: F401

    html_theme = "sphinx_rtd_theme"
except ImportError:
    html_theme = "alabaster"
html_static_path = ["_static"]
html_show_sourcelink = False

htmlhelp_basename = "pystrixdoc"

latex_documents = [
    (
        "index",
        "pystrix.tex",
        "pystrix Documentation",
        re.search(", (.*?) <", module.COPYRIGHT).group(1),
        "manual",
    ),
]
