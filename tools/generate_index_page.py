#!/usr/bin/env python3
"""Generate the unified aggregate landing page — ONE page, two views (#276).

Scans MAP.md files, derives the domain graph ONCE via `tools/lib/domain_graph.py`, and
emits a single page (`library/index.html` by default) with ONE `#page-data` island feeding
two views: an indented WAI-ARIA Tree (primary/default nav) and an iterated dagre Map
(secondary relationship view), toggled client-side and persisted to prefs.

This retires the separate index derivation (the old card-grid) and subsumes the global
forest map: `generate_global_map.py` now emits only a redirect stub → `index.html?view=map`.

Usage:
    python tools/generate_index_page.py                              # auto-scan project root
    python tools/generate_index_page.py --scan-dir library           # scan the library
    python tools/generate_index_page.py --scan-dir library --output library/index.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows cp1252 stdout chokes on the ✓ / — this prints (AGENTS.md Constraints).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
OUTPUT = PROJECT_ROOT / "lessons" / "index.html"

from lib.domain_graph import find_maps, build_domain_graph, build_forest_edges  # noqa: E402
from lib.map_links import map_href  # noqa: E402
from lib.page_template import render_index_page  # noqa: E402


def parse_mission(scan_dir: Path | None) -> dict | None:
    """Parse MISSION.md (title/why/criteria) if a real one exists — index presentation
    logic (kept out of domain_graph, which is view-agnostic). Falls back scan_dir → workspace."""
    mission_path = (scan_dir or PROJECT_ROOT) / "MISSION.md"
    if not mission_path.exists():
        mission_path = PROJECT_ROOT / "workspace" / "MISSION.md"
    if not mission_path.exists():
        return None
    content = mission_path.read_text(encoding="utf-8")
    if "Tell your AI assistant" in content or "[Your Topic]" in content:
        return None  # generic template placeholder
    title_m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    why_m = re.search(r'## Why\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    criteria_m = re.search(r'## Success Criteria\n\n((?:- .+\n?)+)', content)
    criteria = []
    if criteria_m:
        criteria = [line.lstrip('- ').strip()
                    for line in criteria_m.group(1).strip().splitlines() if line.strip()]
    return {
        "title": title_m.group(1).strip() if title_m else None,
        "why": why_m.group(1).strip() if why_m else None,
        "criteria": criteria[:4],
    }


def build_page_data(records: list[dict], output_file: Path, mission: dict | None) -> dict:
    """Project the superset domain-graph records into the ONE #page-data island feeding
    both views. `mapHref` is computed HERE (per output file — it's document-relative to the
    output path, so it can't live in the shared record). Domains carry ALL depths: the Tree
    filters roots (depth==0 & !island) client-side; the Map lays out the whole graph.
    Stats count depth-0 domains only (the index's historical meaning of "domains")."""
    domains = [{
        "slug": r["domain"],
        "title": r["title"],
        "description": r["description"],
        "depth": r["depth"],
        "parent": r["parent"],
        "total": r["total"],
        "complete": r["complete"],
        "inProgress": r["in_progress"],
        "mapHref": map_href(r["path"], output_file, r["domain"]),
    } for r in records]

    edges, islands = build_forest_edges(records)
    roots = [r for r in records if r["depth"] == 0]
    return {
        "domains": domains,
        "edges": edges,
        "islands": islands,
        "mission": mission,
        "stats": {
            "domainCount": len(roots),
            "topicCount": sum(r["total"] for r in roots),
            "completeCount": sum(r["complete"] for r in roots),
        },
    }


_MODULE_SCRIPT = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { UnifiedView } from '../assets/components/UnifiedView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    // View selection: ?view=map wins, else the persisted pref, else 'tree'. Write the
    // resolved value through to prefs so a ?view= visit updates the saved default.
    import { prefs, set as setPref } from '../assets/preferences.js';
    const urlView = new URLSearchParams(location.search).get('view');
    const resolved = urlView === 'map' ? 'map'
      : urlView === 'tree' ? 'tree'
      : (prefs.value.mapView || 'tree');
    if (resolved !== prefs.value.mapView) setPref('mapView', resolved);

    render(
      html`<${UnifiedView} domains=${data.domains} edges=${data.edges} islands=${data.islands}
        stats=${data.stats} mission=${data.mission} />`,
      document.getElementById('app')
    );
"""

_CSS_EXTRA = """
    body { max-width: 900px; margin: 0 auto; padding: 2rem; }
    .index-view h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .index-meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }
    .index-cue { font-size: 0.9rem; margin: 0 0 1rem; }
    .index-cue-start { color: var(--text-muted); }
    .index-cue-resume a {
      display: inline-block; color: var(--accent); font-weight: 600;
      text-decoration: none; padding: 0.5rem 0.9rem; border-radius: 8px;
      background: var(--bg-elevated); border: 1px solid var(--border);
    }
    .index-cue-resume a:hover { border-color: var(--accent); }

    /* Tree | Map toggle */
    .view-toggle { display: inline-flex; gap: 0; margin: 0 0 1.5rem; border: 1px solid var(--border);
      border-radius: 8px; overflow: hidden; }
    .vt-btn { background: var(--bg-elevated); color: var(--text-muted); border: none;
      padding: 0.4rem 1.1rem; font-size: 0.85rem; cursor: pointer; font: inherit; }
    .vt-btn + .vt-btn { border-left: 1px solid var(--border); }
    .vt-btn.is-active { background: var(--accent); color: var(--bg); font-weight: 600; }
    .vt-btn:hover:not(.is-active) { color: var(--text); }

    /* Indented tree view */
    .indented-tree .ti-root { list-style: none; padding-left: 0; margin: 0; }
    .indented-tree .ti-group { list-style: none; margin: 0; padding-left: 1.4rem;
      border-left: 1px solid var(--border); margin-left: 0.7rem; }
    .indented-tree .ti-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0.7rem;
      border-radius: 8px; text-decoration: none; color: var(--text); outline-offset: 2px; }
    .indented-tree .ti-row:hover { background: var(--bg-elevated); }
    .indented-tree .ti-row:focus-visible { outline: 2px solid var(--accent); }
    .indented-tree .ti-row.is-child { color: var(--text-muted); }
    .indented-tree .ti-twisty { background: none; border: none; color: var(--text-muted);
      cursor: pointer; font-size: 0.7rem; padding: 0 0.2rem; line-height: 1; }
    .indented-tree .ti-title { font-weight: 600; }
    .indented-tree .ti-stat { font-size: 0.78rem; color: var(--text-faint); }
    .indented-tree .ti-leads { font-size: 0.75rem; color: var(--text-muted); font-style: italic; }
    .sc-section-title { font-size: 0.9rem; color: var(--text-muted); margin: 1.5rem 0 0.5rem; }

    /* Iterated map view */
    .iterated-map .im-legend { display: flex; gap: 1.5rem; font-size: 0.78rem;
      color: var(--text-muted); margin-bottom: 0.6rem; align-items: center; }
    .iterated-map .im-legend span { display: inline-flex; align-items: center; gap: 0.35rem; }
    .im-card { display: block; padding: 0.8rem 1rem; background: var(--bg-elevated);
      border: 1px solid var(--border); border-radius: 10px; text-decoration: none; color: var(--text);
      transition: border-color 0.15s, box-shadow 0.15s; box-sizing: border-box; }
    .im-card:hover, .im-card:focus-visible { border-color: var(--accent); box-shadow: 0 2px 12px rgba(203,166,247,0.12); }
    .im-card h3 { font-size: 0.95rem; margin: 0 0 0.3rem; display: flex; align-items: center; gap: 0.5rem; }
    .im-card .dc-meta { font-size: 0.78rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.4rem; }
    .im-card.is-child { border-left: 3px solid var(--accent); }
    .dc-sub-badge { font-size: 0.68rem; padding: 0.1rem 0.4rem; border-radius: 3px;
      background: color-mix(in srgb, var(--text-muted) 15%, transparent); color: var(--text-muted); }
    .islands-panel { margin-top: 1.5rem; padding: 1rem; border: 1px dashed var(--border); border-radius: 8px; }
    .islands-panel h2 { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.5rem; }
    .islands-panel ul { list-style: none; padding: 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .islands-panel a { font-size: 0.8rem; padding: 0.3rem 0.6rem; border: 1px solid var(--border);
      border-radius: 4px; color: var(--text-muted); text-decoration: none; }
    .islands-panel a:hover { border-color: var(--accent); color: var(--accent); }
"""


def _parse_args(argv: list[str]) -> tuple[list[Path], Path]:
    scan_dirs = [PROJECT_ROOT]
    output = OUTPUT
    if "--scan-dir" in argv:
        v = Path(argv[argv.index("--scan-dir") + 1])
        scan_dirs = [v if v.is_absolute() else PROJECT_ROOT / v]
    if "--output" in argv:
        v = Path(argv[argv.index("--output") + 1])
        output = v if v.is_absolute() else PROJECT_ROOT / v
    return scan_dirs, output


def main() -> int:
    scan_dirs, output = _parse_args(sys.argv[1:])
    paths = find_maps(scan_dirs)
    records = build_domain_graph(paths)
    mission = parse_mission(scan_dirs[0] if scan_dirs else None)
    data = build_page_data(records, output, mission)

    page = render_index_page(
        body_content='<div id="app"></div>',
        data=data,
        module_script=_MODULE_SCRIPT,
        css_extra=_CSS_EXTRA,
        depth=1,
        include_dagre=True,  # the Map view's dagre layout needs window.dagre ready
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    n_roots = data["stats"]["domainCount"]
    n_nodes, n_edges, n_isl = len(data["domains"]), len(data["edges"]), len(data["islands"])
    print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} "
          f"({n_roots} domains, {n_nodes} nodes, {n_edges} edges, {n_isl} islands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
