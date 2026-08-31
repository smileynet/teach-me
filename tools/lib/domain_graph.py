"""domain_graph.py — the ONE derivation of the domain graph (#276).

Historically `generate_index_page.py` and `generate_global_map.py` each walked the
`MAP.md` files, loaded them via the canonical parser, and computed per-domain completion
from the per-user overlay — duplicating the completion math and diverging on `find_maps`.
#276 unifies the aggregate index and the global/forest map into one two-view page, so the
derivation is extracted here ONCE:

    find_maps(scan_dirs)          -> [Path]        # all depth-0/1 *.MAP.md (skip depth-2+)
    build_domain_graph(paths)     -> [record]      # superset record per map, ALL depths
    build_forest_edges(records)   -> (edges, islands)

A `record` is the SUPERSET both views project from — the index filters `depth == 0` and
maps to its card fields; the forest uses ALL records as nodes plus the edges/islands from
`build_forest_edges`. `mapHref` is deliberately NOT in the record: it's document-relative
to the OUTPUT file (`map_links.map_href` = `os.relpath(target, output_file.parent)`), so the
same domain yields a different href per output path — the caller computes it at data-island
build time. The real MAP.md `path` DOES live in the record because both the overlay-root
inference and the href depend on the `maps/`-parent rule.
"""

from __future__ import annotations

from pathlib import Path

try:
    from tools.map_parser import load_map
    from tools.lib.overlay import status_map_for_map
except ModuleNotFoundError:  # tools/ on sys.path directly (script style)
    from map_parser import load_map  # type: ignore[no-redef]
    from lib.overlay import status_map_for_map  # type: ignore[no-redef]


def find_maps(scan_dirs: list[Path]) -> list[Path]:
    """All `*.MAP.md` under the scan dirs (root + direct + recursive), skipping depth-2+
    sub-maps (identified by the `--` stem separator).

    One canonical implementation (adopts the index's fuller version — root `MAP.md`, a
    direct-dir `*.MAP.md` glob, then a recursive `rglob` — replacing the forest's thinner
    rglob-only copy).
    """
    maps: list[Path] = []
    for d in scan_dirs:
        root_map = d / "MAP.md"
        if root_map.exists() and root_map not in maps:
            maps.append(root_map)
        for f in sorted(d.glob("*.MAP.md")):
            if "--" not in f.stem and f not in maps:
                maps.append(f)
        for f in sorted(d.rglob("*.MAP.md")):
            if "--" not in f.stem and f not in maps:
                maps.append(f)
    return maps


def _description(dm) -> str:
    """First sentence of the orientation (with a trailing '.'), else the frontmatter
    description. Index-facing; the forest ignores it."""
    if dm.orientation:
        return dm.orientation.split(".", 1)[0].strip() + "."
    return dm.description


def build_domain_graph(paths: list[Path]) -> list[dict]:
    """Load each MAP.md once and return one SUPERSET record per map (ALL depths).

    Completion is computed once here (killing the duplicated `parse_map_meta` /
    `_completion` math). Depth filtering is left to each view: the index keeps
    `depth == 0`, the forest keeps depth-0 AND depth-1 sub-maps as nodes.
    """
    records: list[dict] = []
    for p in paths:
        dm = load_map(p)
        status_map = status_map_for_map(p)
        records.append({
            "path": p,  # source MAP.md — needed for map_href + overlay root (maps/-parent rule)
            "domain": dm.domain,
            "title": dm.title or dm.domain.replace("-", " ").title(),
            "description": _description(dm),
            "depth": dm.depth,
            "parent": dm.parent,
            "leads_to": list(dm.leads_to),
            "total": len(dm.topics),
            "complete": sum(1 for t in dm.topics if status_map.get(t.id) == "complete"),
            "in_progress": sum(1 for t in dm.topics if status_map.get(t.id) == "in-progress"),
        })
    return records


def build_forest_edges(records: list[dict]) -> tuple[list[dict], list[str]]:
    """Structural edges + islands from the superset records (forest-only).

    parent/child: a depth-1 sub-map (`parent`) → its parent domain.
    leads_to: the frontmatter `leads_to` list, resolved against known domains (danglers
    pointing at not-yet-created domains are dropped). Islands = domains no edge touches.
    """
    by_domain = {r["domain"] for r in records}
    edges: list[dict] = []
    for r in records:
        if r["parent"] and r["parent"] in by_domain:
            edges.append({"source": r["parent"], "target": r["domain"], "type": "parent"})
        for lt in r["leads_to"]:
            if lt.slug in by_domain and lt.slug != r["domain"]:
                edges.append({"source": r["domain"], "target": lt.slug,
                              "type": "leads_to", "why": lt.why})
    connected = {e["source"] for e in edges} | {e["target"] for e in edges}
    islands = sorted(r["domain"] for r in records if r["domain"] not in connected)
    return edges, islands
