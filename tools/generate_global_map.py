#!/usr/bin/env python3
"""Generate the global/forest map — a domain-level overview of all MAP.md in a scan-dir.

Each node is a DOMAIN (sized by topic count, colored by per-user overlay completion).
Edges are STRUCTURAL only (#155 Phase 1 — higher precision than concept similarity):
  - parent/child: a depth-1 sub-map (DomainMap.parent) → its parent domain
  - leads_to: the frontmatter `leads_to` list (navigational), resolved against known domains
Domains with no edges are ISLANDS — surfaced (sidebar + separate placement), not errors.
Clicking a domain navigates to its per-domain map page.

Concept-similarity edges are deferred to Phase 2 (author-confirmed suggestions).

Usage:
    python tools/generate_global_map.py --scan-dir examples --output lessons/global-map.html
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
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from map_parser import load_map, DomainMap  # noqa: E402
from lib.overlay import status_map_for_map  # noqa: E402
from lib.page_template import render_map_page  # noqa: E402


def find_maps(scan_dir: Path) -> list[Path]:
    """All *.MAP.md under scan_dir (root, direct, recursive), skipping depth-2+ (`--`)."""
    maps: list[Path] = []
    root = scan_dir / "MAP.md"
    if root.exists():
        maps.append(root)
    for f in sorted(scan_dir.rglob("*.MAP.md")):
        if "--" not in f.stem and f not in maps:
            maps.append(f)
    return maps


def _completion(dm: DomainMap, map_path: Path) -> tuple[int, int, int]:
    """(complete, in_progress, total) from the per-user overlay (matches the index)."""
    status_map = status_map_for_map(map_path)
    total = len(dm.topics)
    complete = sum(1 for t in dm.topics if status_map.get(t.id) == "complete")
    in_progress = sum(1 for t in dm.topics if status_map.get(t.id) == "in-progress")
    return complete, in_progress, total


def build_forest(scan_dir: Path) -> dict:
    """Load all maps, synthesize domain nodes + structural edges + islands."""
    paths = find_maps(scan_dir)
    loaded = [(p, load_map(p)) for p in paths]
    by_domain = {dm.domain: (p, dm) for p, dm in loaded}

    # A domain's map page lives at {workspace}/lessons/{domain}-map.html. Record the
    # workspace-relative link so the client can navigate (cross-workspace links are the
    # known #198 limitation — we still emit the intended target).
    nodes = []
    for p, dm in loaded:
        complete, in_progress, total = _completion(dm, p)
        workspace = p.parent.parent if p.parent.name == "maps" else p.parent
        map_href = f"{workspace.name}/lessons/{dm.domain}-map.html"
        nodes.append({
            "slug": dm.domain,
            "title": dm.title or dm.domain.replace("-", " ").title(),
            "depth": dm.depth,
            "parent": dm.parent,
            "total": total,
            "complete": complete,
            "inProgress": in_progress,
            "mapHref": map_href,
        })

    # Structural edges: parent/child + leads_to. Resolve targets against known domains;
    # drop danglers (a leads_to pointing at a not-yet-created domain).
    edges = []
    for p, dm in loaded:
        if dm.parent and dm.parent in by_domain:
            edges.append({"source": dm.parent, "target": dm.domain, "type": "parent"})
        for lt in dm.leads_to:
            if lt.slug in by_domain and lt.slug != dm.domain:
                edges.append({"source": dm.domain, "target": lt.slug,
                              "type": "leads_to", "why": lt.why})

    # Islands = domains touched by no edge (neither endpoint).
    connected = {e["source"] for e in edges} | {e["target"] for e in edges}
    islands = sorted(n["slug"] for n in nodes if n["slug"] not in connected)

    return {"domains": nodes, "edges": edges, "islands": islands}


def _module_script(depth: int) -> str:
    prefix = "../" * depth
    return f"""
    import {{ h, render }} from 'preact';
    import htm from 'htm';
    import {{ GlobalMapView }} from '{prefix}assets/components/GlobalMapView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${{GlobalMapView}} domains=${{data.domains}} edges=${{data.edges}} islands=${{data.islands}} />`,
      document.getElementById('app')
    );
"""


_CSS_EXTRA = """
    body { max-width: none; padding: 2rem; }
    /* Horizontal scroll affordance (#269): a right-edge fade cues that the forest
       extends beyond the viewport when the canvas is wider than the container. */
    .dag-scroll { position: relative; }
    .dag-scroll::after {
      content: ""; position: absolute; top: 0; right: 0; width: 48px; height: 100%;
      pointer-events: none; z-index: 3;
      background: linear-gradient(to right, transparent, var(--bg));
    }
    .dag-container { position: relative; width: 100%; overflow-x: auto; scrollbar-width: thin; }
    .dag-canvas { position: relative; min-width: min-content; }
    .edge-layer { position: absolute; top: 0; left: 0; pointer-events: none; z-index: 1; }
    .domain-card {
      position: absolute; width: 300px; padding: 1rem 1.2rem;
      background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px;
      z-index: 2; text-decoration: none; color: inherit;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .domain-card:hover { border-color: var(--accent); box-shadow: 0 2px 16px rgba(203,166,247,0.1); }
    .domain-card h3 { font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }
    .domain-card .dc-meta { font-size: 0.78rem; color: var(--text-muted); }
    .domain-card .dc-ring { display: inline-flex; }
    /* Sub-map distinction: a subtle left accent (NOT a dashed all-round border, which
       read as a highlighted/selected state in the audit). Border color stays --border. */
    .domain-card.is-child { border-left: 3px solid var(--accent); }
    .dc-sub-badge { font-size: 0.68rem; padding: 0.1rem 0.4rem; border-radius: 3px;
      background: color-mix(in srgb, var(--text-muted) 15%, transparent); color: var(--text-muted); }
    .islands-panel { margin-top: 2rem; padding: 1rem; border: 1px dashed var(--border); border-radius: 8px; }
    .islands-panel h2 { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.5rem; }
    .islands-panel ul { list-style: none; padding: 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .islands-panel a { font-size: 0.8rem; padding: 0.3rem 0.6rem; border: 1px solid var(--border);
      border-radius: 4px; color: var(--text-muted); text-decoration: none; }
    .islands-panel a:hover { border-color: var(--accent); color: var(--accent); }
"""


def main() -> int:
    args = sys.argv[1:]
    scan_dir = PROJECT_ROOT / "examples"
    output = PROJECT_ROOT / "lessons" / "global-map.html"
    if "--scan-dir" in args:
        i = args.index("--scan-dir")
        scan_dir = Path(args[i + 1])
        if not scan_dir.is_absolute():
            scan_dir = PROJECT_ROOT / scan_dir
    if "--output" in args:
        i = args.index("--output")
        output = Path(args[i + 1])
        if not output.is_absolute():
            output = PROJECT_ROOT / output

    data = build_forest(scan_dir)
    depth = 1  # lessons/global-map.html

    html = render_map_page(
        title="Global Map",
        domain="All Domains",
        domain_slug="global",
        body_content='  <div id="app"></div>',
        data=data,
        module_script=_module_script(depth),
        css_extra=_CSS_EXTRA,
        depth=depth,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    n, e, isl = len(data["domains"]), len(data["edges"]), len(data["islands"])
    print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} "
          f"({n} domains, {e} edges, {isl} islands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
