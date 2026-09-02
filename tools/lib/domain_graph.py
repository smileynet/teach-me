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

The record also carries `topic_ids` (#279): the ULIDs this domain owns, so a load-time
overlay read in the browser can recompute counts against the ULID-keyed overlay. The baked
`complete`/`in_progress` integers remain the demo/no-JS floor — the client overrides them
only when a real user overlay exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from tools.map_parser import load_map
    from tools.lib.overlay import demo_status_map_for_map as status_map_for_map
except ModuleNotFoundError:  # tools/ on sys.path directly (script style)
    from map_parser import load_map  # type: ignore[no-redef]
    from lib.overlay import demo_status_map_for_map as status_map_for_map  # type: ignore[no-redef]


# --- Visibility (single source of truth: discovery provenance, not a stored flag) ---
#
# A topic's visibility IS where its MAP.md was discovered — committed `library/` vs the
# gitignored `.user/` overlay (#184, ADR 0012). We do NOT store `private: bool` on Topic
# (map_parser.py); a flag beside a `.user/`-sourced path is a second source that can drift.
# The domain-graph record carries a carried-data variant assigned ONCE at discovery
# (parse-at-boundary). Variant not bool because it gates three behaviours: the private
# badge, the shared->private prereq ban, and never baking private content into a committed page.


@dataclass(frozen=True)
class Shared:
    """A committed, versioned topic under `library/` — the default, everyone gets on clone."""
    path: Path  # the committed MAP.md


@dataclass(frozen=True)
class Private:
    """A local-only topic under `.user/` — never committed, overlaid at render/serve time."""
    path: Path            # the `.user/maps/*.MAP.md` overlay source
    promote_target: Path  # where a `--promote` move would land it (the committed sibling)


Visibility = Shared | Private


def is_private(v: Visibility) -> bool:
    return isinstance(v, Private)


def find_maps(scan_dirs: list[Path]) -> list[Path]:
    """All committed `*.MAP.md` under the scan dirs (root + direct + recursive), skipping
    depth-2+ sub-maps (the `--` stem separator) and the private `.user/` overlay.

    One canonical implementation (adopts the index's fuller version — root `MAP.md`, a
    direct-dir `*.MAP.md` glob, then a recursive `rglob`). Private overlays are found
    separately by `find_private_maps` (#184).
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
            if "--" not in f.stem and ".user" not in f.parts and f not in maps:
                maps.append(f)
    return maps


def find_private_maps(scan_dirs: list[Path]) -> list[Path]:
    """All private-overlay `*.MAP.md` under `.user/maps/` (#184).

    Private topic maps live at `{scan}/.user/maps/{domain}.MAP.md` (gitignored) — the ONLY
    place private topics appear. Committed `library/` maps never reference them. Same
    depth-2+ skip as `find_maps`.
    """
    maps: list[Path] = []
    for d in scan_dirs:
        user_maps = d / ".user" / "maps"
        if not user_maps.exists():
            continue
        for f in sorted(user_maps.rglob("*.MAP.md")):
            if "--" not in f.stem and f not in maps:
                maps.append(f)
    return maps


def _description(dm) -> str:
    """First sentence of the orientation (with a trailing '.'), else the frontmatter
    description. Index-facing; the forest ignores it."""
    if dm.orientation:
        return dm.orientation.split(".", 1)[0].strip() + "."
    return dm.description


def _build_record(p: Path, source: Visibility) -> dict:
    """One superset record for a single MAP.md (`p`), tagged with its visibility `source`."""
    dm = load_map(p)
    status_map = status_map_for_map(p)
    private = is_private(source)
    return {
        "path": p,  # source MAP.md — needed for map_href + overlay root (maps/-parent rule)
        "source": source,  # Shared | Private — visibility, assigned ONCE here (#184)
        "private": private,  # convenience flag DERIVED from source (not a second source)
        "domain": dm.domain,
        "title": dm.title or dm.domain.replace("-", " ").title(),
        "description": _description(dm),
        "depth": dm.depth,
        "parent": dm.parent,
        "leads_to": list(dm.leads_to),
        "total": len(dm.topics),
        "complete": sum(1 for t in dm.topics if status_map.get(t.id) == "complete"),
        "in_progress": sum(1 for t in dm.topics if status_map.get(t.id) == "in-progress"),
        "topic_ids": [t.id for t in dm.topics],
        # Private topics NEVER seed the committed demo (they don't ship); shared topics do.
        "demo_status": {} if private else {t.id: status_map[t.id] for t in dm.topics if t.id in status_map},
        # Private prereq targets, for the shared->private guard (E) + private-only detection.
        "prereq_ids": [pr for t in dm.topics for pr in t.prereqs],
    }


def build_domain_graph(paths: list[Path], private_paths: list[Path] | None = None) -> list[dict]:
    """Load each MAP.md once and return one SUPERSET record per map (ALL depths).

    Committed `paths` (from `find_maps`) become `Shared` records. Optional `private_paths`
    (from `find_private_maps`, #184) become `Private` records. A private map whose `domain`
    matches a committed one is MERGED into that committed record (its topics extend the
    domain locally, marked private); a private map with no committed sibling becomes its own
    `Private` domain record. Completion is computed once here.
    """
    records: list[dict] = [_build_record(p, Shared(p)) for p in paths]

    for pp in private_paths or []:
        # promote target: the committed sibling this private map would move to on --promote.
        # `.user/maps/{name}.MAP.md` -> `{workspace}/{name}.MAP.md` (workspace = .user's parent).
        workspace = pp.parent.parent.parent if pp.parent.name == "maps" else pp.parent
        prec = _build_record(pp, Private(pp, promote_target=workspace / pp.name))
        host = next((r for r in records if r["domain"] == prec["domain"] and not r["private"]), None)
        if host is not None:
            _merge_private_into(host, prec)
        else:
            records.append(prec)  # wholly-private domain
    return records


def _merge_private_into(host: dict, prec: dict) -> None:
    """Extend a committed domain record with a private overlay's topics (local-only).

    The committed record's OWN counts/topic_ids stay first (shared truth); private topics
    append and are tracked separately in `private_topic_ids` so the client/badge can mark
    them without polluting the shared `topic_ids` join key or the demo seed.
    """
    host["total"] += prec["total"]
    host["complete"] += prec["complete"]
    host["in_progress"] += prec["in_progress"]
    host["topic_ids"] = host["topic_ids"] + prec["topic_ids"]
    host.setdefault("private_topic_ids", []).extend(prec["topic_ids"])
    host["has_private"] = True


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
