#!/usr/bin/env python3
"""Forest prereq-validation gate (#155 Phase 1 / closes #260).

Single-map `validate()` flags a prereq that lives in a SIBLING map as an "undefined
prereq" (its slug set is one file only). But cross-map prereqs are a valid authoring
construct — a depth-1 sub-map can prereq a topic in its parent/sibling (e.g. godot-mktoon's
`configurable-banding` prereqs `toon-banding` from godot-toon-shaders). This gate validates
each domain's map SET together via `map_parser.validate_forest`, so those references
resolve against the union of the domain's maps.

A "domain map set" = all `*.MAP.md` under one workspace's `maps/` dir (the parent map +
its depth-1 children share a forest). Cross-WORKSPACE references are out of scope here.

Structured JSON to stdout; exit 0 = all forests clean, 1 = a real dangling/cycle/ambiguity,
2 = error.

Usage:
    python tools/check-maps-forest.py            # all example workspaces
    python tools/check-maps-forest.py --json
    python tools/check-maps-forest.py --scan-dir library/godot-gamedev
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from map_parser import load_map, validate_forest  # noqa: E402


def _maps_dirs(scan: Path) -> list[Path]:
    """Every committed `maps/` dir under scan that holds at least one *.MAP.md.

    Excludes the private `.user/` overlay (#184): private topic maps are validated in
    isolation and are NEVER part of a committed forest. This also means a committed map
    that prereqs a private-only topic fails here as an 'undefined prereq' — which IS the
    shared->private prereq ban (a committed topic cannot depend on private content).
    """
    return sorted({p.parent for p in scan.rglob("maps/*.MAP.md") if ".user" not in p.parts})


def main() -> int:
    args = sys.argv[1:]
    json_only = "--json" in args
    scan = ROOT / "library"
    if "--scan-dir" in args:
        i = args.index("--scan-dir")
        if i + 1 < len(args):
            scan = Path(args[i + 1])
            if not scan.is_absolute():
                scan = ROOT / scan

    results = []
    exit_code = 0
    for maps_dir in _maps_dirs(scan):
        paths = sorted(maps_dir.glob("*.MAP.md"))
        maps = [load_map(p) for p in paths]
        errors = validate_forest(maps)
        ok = not errors
        if not ok:
            exit_code = 1
        results.append({
            "workspace": str(maps_dir.parent.relative_to(ROOT)),
            "maps": [m.domain for m in maps],
            "ok": ok,
            "errors": errors,
        })
        if not json_only:
            mark = "OK " if ok else "FAIL"
            print(f"  [{mark}] {maps_dir.parent.name}: {len(maps)} map(s) — "
                  f"{'clean' if ok else str(len(errors)) + ' error(s)'}")
            for e in errors:
                print(f"        - {e}")

    if json_only:
        print(json.dumps({"status": "pass" if exit_code == 0 else "fail",
                          "forests": results}, indent=2))
    elif exit_code == 0:
        print(f"\nAll {len(results)} domain map-set(s) validate clean (forest prereq check).")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
