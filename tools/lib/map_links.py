"""map_links.py — one place that computes the href to a domain's map page (#198).

Both the aggregate index and the global/forest map link to per-domain map pages that
live under each workspace (`{workspace}/lessons/{domain}-map.html`), while the linking
page itself lives elsewhere (e.g. project-root `lessons/index.html`, or the library root).
A bare `{domain}-map.html` (index) or `{workspace.name}/lessons/...` (global map) 404s.

The fix is a DOCUMENT-RELATIVE href computed from the two real on-disk paths, so it
resolves identically under a local server AND static GitHub Pages (root-relative `/...`
breaks on project-pages' `/{repo}/` base path — see research). Pure pathlib/os, no deps.
"""

from __future__ import annotations

import os
from pathlib import Path


def domain_map_path(map_path: Path, domain: str) -> Path:
    """On-disk path of the generated `{domain}-map.html` for a source MAP.md.

    A MAP.md lives at `{workspace}/maps/...`; its map page is generated to
    `{workspace}/lessons/{domain}-map.html`.
    """
    map_path = Path(map_path)
    workspace = map_path.parent.parent if map_path.parent.name == "maps" else map_path.parent
    return workspace / "lessons" / f"{domain}-map.html"


def map_href(map_path: Path, output_file: Path, domain: str) -> str:
    """Document-relative POSIX URL from `output_file` (the index/global HTML) to the
    per-domain map page generated for `map_path`.

    Relative (not root-relative) so it works both on localhost and GitHub project pages.
    """
    target = domain_map_path(map_path, domain)
    rel = os.path.relpath(target, start=Path(output_file).parent)
    return Path(rel).as_posix()
