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

from lib.domain_graph import find_maps, find_private_maps, build_domain_graph, build_forest_edges  # noqa: E402
from lib.map_links import map_href  # noqa: E402
from lib.page_template import render_index_page  # noqa: E402


def parse_mission(scan_dir: Path | None) -> dict | None:
    """Parse MISSION.md (title/why/criteria) if a real one exists — index presentation
    logic (kept out of domain_graph, which is view-agnostic).

    Only the default whole-project scan (scan_dir is None / PROJECT_ROOT) inherits the
    single-workspace mission at workspace/MISSION.md. A specific --scan-dir (a per-domain
    index generate) must NOT borrow workspace/MISSION.md — that file is gitignored and
    machine-local, so inheriting it makes the committed per-domain page non-reproducible
    (drifts per machine) and gives it another domain's mission (cross-scope bleed, #316)."""
    base = scan_dir or PROJECT_ROOT
    mission_path = base / "MISSION.md"
    if not mission_path.exists() and base == PROJECT_ROOT:
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
        # Join key for the load-time overlay read (#279): the topic ULIDs this domain
        # owns. The client counts statuses from the user's overlay against these ids to
        # override the baked demo counts above. Absent a real overlay, the baked values
        # stand (demo / no-JS floor).
        "topicIds": r["topic_ids"],
        # Private-overlay flags (#184): `private` = the whole domain is local-only;
        # `hasPrivate` = a committed domain carries some private topics; `privateTopicIds`
        # lets the view badge exactly those. Private content never ships — these are only
        # ever non-empty when a local `.user/` overlay was present at generate/serve time.
        "private": r.get("private", False),
        "hasPrivate": r.get("has_private", False),
        "privateTopicIds": r.get("private_topic_ids", []),
    } for r in records]

    edges, islands = build_forest_edges(records)
    roots = [r for r in records if r["depth"] == 0]
    # Demo seed (#279): flat {topic_id → status} union across ALL domains, inlined so the
    # demo floor travels IN page-data. The client seeds the demo view from this map and,
    # on user takeover (hasOwnProgress), ignores it in favour of the user's own overlay.
    demo_overlay: dict[str, str] = {}
    for r in records:
        demo_overlay.update(r["demo_status"])
    return {
        "domains": domains,
        "edges": edges,
        "islands": islands,
        "mission": mission,
        "demoOverlay": demo_overlay,
        "stats": {
            "domainCount": len(roots),
            "topicCount": sum(r["total"] for r in roots),
            "completeCount": sum(r["complete"] for r in roots),
            "inProgressCount": sum(r["in_progress"] for r in roots),
        },
    }


_MODULE_SCRIPT = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { UnifiedView } from '../assets/components/UnifiedView.js';
    import { prefs, set as setPref } from '../assets/preferences.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    // View selection: ?view=map wins, else the persisted pref, else 'tree'. Write the
    // resolved value through to prefs so a ?view= visit updates the saved default.
    const urlView = new URLSearchParams(location.search).get('view');
    const resolved = urlView === 'map' ? 'map'
      : urlView === 'tree' ? 'tree'
      : (prefs.value.mapView || 'tree');
    if (resolved !== prefs.value.mapView) setPref('mapView', resolved);

    // Load-time progress resolution (#279). The baked domains[*].{complete,inProgress} and
    // stats are the DEMO / no-JS floor. If the user has their OWN overlay (served hosts
    // only — GET /api/overlay), recompute counts from it and swap. Read-then-swap: keep the
    // baked floor unless a real overlay actually resolves. Static hosts (GH Pages) 404 the
    // fetch, so the demo counts stand (Option A: static = display-only demo).
    async function resolveProgress() {
      // hasOwnProgress means the user has taken over from the demo; from then on the demo
      // seed is never shown — an absent/empty overlay yields all-not-started (empty view).
      const owns = prefs.value.hasOwnProgress === true;
      let overlay = null;
      try {
        const res = await fetch('api/overlay', { headers: { accept: 'application/json' } });
        if (res.ok) overlay = (await res.json()).overlay || {};
      } catch (_) { /* static host / no server — keep the demo floor */ }

      // Only override when we have a real signal: either the user owns their progress, or a
      // non-empty overlay came back. An empty overlay on a non-owning user = show the demo.
      const hasReal = owns || (overlay && Object.keys(overlay).length > 0);
      if (!hasReal) {
        // Demo floor stands. Flag it so the view can offer the takeover action — but only
        // if the demo actually shows progress (a zero demo has nothing to "take over").
        const demoHasProgress = data.stats.completeCount > 0 || (data.stats.inProgressCount || 0) > 0;
        return demoHasProgress;
      }
      const map = overlay || {};

      let cComplete = 0, cInProgress = 0;
      for (const d of data.domains) {
        const ids = d.topicIds || [];
        d.complete = ids.filter(id => map[id] === 'complete').length;
        d.inProgress = ids.filter(id => map[id] === 'in-progress').length;
        if (d.depth === 0) { cComplete += d.complete; cInProgress += d.inProgress; }
      }
      data.stats = { ...data.stats, completeCount: cComplete, inProgressCount: cInProgress };
      return false;  // real data resolved — no demo banner
    }

    const showingDemo = await resolveProgress();

    render(
      html`<${UnifiedView} domains=${data.domains} edges=${data.edges} islands=${data.islands}
        stats=${data.stats} mission=${data.mission} showingDemo=${showingDemo} />`,
      document.getElementById('app')
    );
"""

# Single-domain landing (#281). A per-domain lessons/index.html is ONE domain's overview,
# not a multi-item index — so it renders the clean IndexView card (no Tree|Map toggle, which
# carries no value for a single zero-edge node). Keeps the #279 load-time count override
# (resolveProgress against the one domain's topicIds) so live progress still works on served
# hosts; drops the view-resolution block (no toggle) and the demo-takeover banner (a
# library-wide action — aggregate-only). include_dagre is False on this path (no Map view).
_INDEX_MODULE_SCRIPT = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { IndexView } from '../assets/components/IndexView.js';
    import { prefs } from '../assets/preferences.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    // Load-time progress resolution (#279/#281). Baked domains[*].{complete,inProgress} are
    // the demo/no-JS floor; override from the user's own overlay (served hosts) against each
    // domain's topicIds. Read-then-swap: keep the floor unless a real overlay resolves.
    async function resolveProgress() {
      const owns = prefs.value.hasOwnProgress === true;
      let overlay = null;
      try {
        const res = await fetch('api/overlay', { headers: { accept: 'application/json' } });
        if (res.ok) overlay = (await res.json()).overlay || {};
      } catch (_) { /* static host / no server — keep the demo floor */ }
      const hasReal = owns || (overlay && Object.keys(overlay).length > 0);
      if (!hasReal) return;
      const map = overlay || {};
      let cComplete = 0, cInProgress = 0;
      for (const d of data.domains) {
        const ids = d.topicIds || [];
        d.complete = ids.filter(id => map[id] === 'complete').length;
        d.inProgress = ids.filter(id => map[id] === 'in-progress').length;
        cComplete += d.complete; cInProgress += d.inProgress;
      }
      data.stats = { ...data.stats, completeCount: cComplete, inProgressCount: cInProgress };
    }

    await resolveProgress();

    render(
      html`<${IndexView} domains=${data.domains} stats=${data.stats} mission=${data.mission} />`,
      document.getElementById('app')
    );
"""

_CSS_EXTRA = """
    body { max-width: 900px; margin: 0 auto; padding: 2rem; }
    .index-view h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .index-meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }
    .index-cue { font-size: 0.9rem; margin: 0 0 1rem; }
    .index-cue-start { color: var(--text-muted); }
    .index-cue-done { color: var(--success); font-weight: 500; }
    .index-cue-resume a {
      display: inline-block; color: var(--accent); font-weight: 600;
      text-decoration: none; padding: 0.5rem 0.9rem; border-radius: 8px;
      background: var(--bg-elevated); border: 1px solid var(--border);
    }
    .index-cue-resume a:hover { border-color: var(--accent); }

    /* Demo takeover note (#279) */
    .index-demo-note { font-size: 0.82rem; color: var(--text-muted); margin: 0 0 1rem;
      display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
    .index-demo-start { background: none; border: 1px solid var(--border); color: var(--accent);
      font: inherit; font-size: 0.8rem; cursor: pointer; padding: 0.25rem 0.7rem; border-radius: 6px; }
    .index-demo-start:hover { border-color: var(--accent); }

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
    .indented-tree .ti-stat { font-size: 0.78rem; color: var(--text-faint); font-variant-numeric: tabular-nums; }
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
    .im-card .dc-meta { font-size: 0.78rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.4rem; font-variant-numeric: tabular-nums; }
    .im-card.is-child { border-left: 3px solid var(--accent); }
    .dc-sub-badge { font-size: 0.68rem; padding: 0.1rem 0.4rem; border-radius: 3px;
      background: color-mix(in srgb, var(--text-muted) 15%, transparent); color: var(--text-muted); }
    /* Private overlay badge (#184) — distinct from sub-map; text label carries the meaning
       (WCAG: not color-alone), amber border signals "local, not shipped". */
    .dc-private-badge { font-size: 0.68rem; padding: 0.1rem 0.4rem; border-radius: 3px;
      border: 1px solid var(--warning, #d08770); color: var(--warning, #d08770);
      background: color-mix(in srgb, var(--warning, #d08770) 12%, transparent); }
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
    private_paths = find_private_maps(scan_dirs)  # .user/ overlay (#184) — local-only
    records = build_domain_graph(paths, private_paths)
    mission = parse_mission(scan_dirs[0] if scan_dirs else None)
    data = build_page_data(records, output, mission)

    # Single-domain landing (#281): one root domain, no cross-domain edges → the Tree|Map
    # toggle carries no value (nothing to navigate BETWEEN). Emit the clean IndexView card
    # instead of the unified two-view page. The aggregate (multiple domains / any edges)
    # keeps UnifiedView. Presence-of-edges is the discriminator, not node count alone.
    single = data["stats"]["domainCount"] <= 1 and not data["edges"]
    module_script = _INDEX_MODULE_SCRIPT if single else _MODULE_SCRIPT

    page = render_index_page(
        body_content='<div id="app"></div>',
        data=data,
        module_script=module_script,
        css_extra=_CSS_EXTRA,
        depth=1,
        include_dagre=not single,  # only the Map view needs window.dagre
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    n_roots = data["stats"]["domainCount"]
    n_nodes, n_edges, n_isl = len(data["domains"]), len(data["edges"]), len(data["islands"])
    kind = "single-domain IndexView" if single else "unified Tree|Map"
    print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} [{kind}] "
          f"({n_roots} domains, {n_nodes} nodes, {n_edges} edges, {n_isl} islands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
