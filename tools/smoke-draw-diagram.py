#!/usr/bin/env python3
"""Smoke-test draw-diagram.py without passing JSON through the shell.

The mise `verify` task previously invoked draw-diagram.py with an inline
`--data '{...}'` argument. That JSON survives bash quoting but is mangled by
mise's Windows inline shell (cmd), producing "invalid JSON in --data". This
wrapper builds the data in Python and invokes the diagram functions directly,
so there is no shell quoting to get wrong on any platform.

Exit 0 if a diagram renders to SVG; non-zero on any failure.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DRAW = TOOLS / "draw-diagram.py"

# draw-diagram.py has a hyphen in its name, so import it by path.
spec = importlib.util.spec_from_file_location("draw_diagram", DRAW)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

data = {
    "nodes": [
        {"label": "A", "color": "blue"},
        {"label": "B", "color": "green"},
    ],
    "arrows": ["test"],
}

diagram = mod.DIAGRAM_TYPES["flow"](data)
svg = diagram.as_svg()

if "<svg" not in svg:
    print("draw-diagram smoke test FAILED: no <svg> in output", file=sys.stderr)
    sys.exit(1)

print("draw-diagram.py OK")
