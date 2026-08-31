#!/usr/bin/env python3
"""Emit the `global-map.html` compatibility redirect stub (#276).

The global/forest map was unified into the aggregate landing page as its Map view
(`generate_index_page.py` → one page, Tree | Map toggle over one #page-data island). This
script no longer builds a separate forest page — it writes a tiny HTML stub that redirects
`global-map.html` → `index.html?view=map`, so any bookmarked/old link lands on the map view.

Document-relative target (no `<base>`) so it survives GitHub project-pages' `/{repo}/` subpath.

Usage:
    python tools/generate_global_map.py --scan-dir library --output library/global-map.html
    mise run map:global
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_STUB = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=index.html?view=map">
  <link rel="canonical" href="index.html?view=map">
  <title>Global Map</title>
</head>
<body>
  <p>The global map is now a view of the <a href="index.html?view=map">All Lessons page</a>&hellip;</p>
</body>
</html>
"""


def main() -> int:
    args = sys.argv[1:]
    output = PROJECT_ROOT / "lessons" / "global-map.html"
    if "--scan-dir" in args:
        pass  # accepted for CLI compat; the stub needs no scan
    if "--output" in args:
        v = Path(args[args.index("--output") + 1])
        output = v if v.is_absolute() else PROJECT_ROOT / v
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_STUB, encoding="utf-8")
    print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} (redirect stub → index.html?view=map)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
