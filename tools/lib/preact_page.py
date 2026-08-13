"""Preact page shell helper — generates HTML boilerplate for Preact pages.

Usage:
    from tools.lib.preact_page import render_page

    html = render_page(
        title="Map: My Domain",
        data={"topics": [...], "edges": [...]},
        module_script='import { MapView } from "../assets/components/MapView.js"; ...',
        css_extra="...",
        body_before="<h1>Title</h1><p>Orientation</p>",
    )
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMPORT_MAP_PATH = PROJECT_ROOT / "assets" / "import-map.json"


def _load_import_map(depth: int = 1) -> str:
    """Load import map JSON and adjust relative paths for page depth.

    depth=1 means page is in lessons/ (one level below root).
    depth=0 means page is at root.
    """
    raw = json.loads(IMPORT_MAP_PATH.read_text())
    prefix = "../" * depth
    adjusted = {}
    for key, val in raw["imports"].items():
        if val.startswith("./"):
            adjusted[key] = prefix + val[2:]
        else:
            adjusted[key] = val
    return json.dumps({"imports": adjusted}, indent=2)


def render_page(
    title: str,
    data: dict | list | None = None,
    module_script: str = "",
    css_extra: str = "",
    body_before: str = "",
    body_after: str = "",
    depth: int = 1,
    include_dagre: bool = False,
) -> str:
    """Generate a self-contained Preact HTML page.

    Args:
        title: Page <title>
        data: JSON-serializable data for the data island (None = no data island)
        module_script: ES module code to run (imports + render call)
        css_extra: Additional <style> block content
        body_before: HTML before the #app mount point
        body_after: HTML after the #app mount point
        depth: Directory depth from project root (1 = lessons/, 2 = lessons/quiz/)
        include_dagre: Whether to include dagre.min.js script tag
    """
    prefix = "../" * depth
    import_map = _load_import_map(depth)

    data_island = ""
    if data is not None:
        data_json = json.dumps(data, ensure_ascii=False)
        data_island = f'  <script type="application/json" id="page-data">{data_json}</script>\n'

    dagre_script = ""
    if include_dagre:
        dagre_script = f'  <script src="{prefix}assets/vendor/dagre.min.js"></script>\n'

    style_block = ""
    if css_extra:
        style_block = f"  <style>\n{css_extra}\n  </style>\n"

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="{prefix}assets/style.css">
{style_block}  <script type="importmap">
{import_map}
  </script>
</head>
<body>
{dagre_script}{data_island}  {body_before}
  <div id="app"></div>
  {body_after}

  <script type="module">
{module_script}
  </script>
</body>
</html>"""
