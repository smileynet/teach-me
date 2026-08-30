#!/usr/bin/env python3
"""Generate the All Lessons index page from MAP.md files.

Scans for MAP.md files (depth 0 only), extracts domain metadata and
topic statuses, and produces a card grid dashboard at lessons/index.html.

Usage:
    python tools/generate_index_page.py                    # auto-scan
    python tools/generate_index_page.py --scan-dir .scratch/spike-041  # custom scan dir
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

# Windows cp1252 stdout chokes on the ✓ this prints (AGENTS.md Constraints).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "lessons" / "index.html"

# Single canonical parser (#256).
try:
    from tools.map_parser import load_map as mp_load_map
except ModuleNotFoundError:
    from map_parser import load_map as mp_load_map  # type: ignore[no-redef]


def _overlay_status_map(map_path: Path) -> dict:
    """{node_id → status} from the per-user overlay for the map's workspace.

    Thin wrapper over the shared `overlay.status_map_for_map` (#155 extraction) so the
    index, per-domain, and global map share one resolution.
    """
    try:
        from tools.lib.overlay import status_map_for_map
    except ModuleNotFoundError:
        from lib.overlay import status_map_for_map  # type: ignore[no-redef]
    return status_map_for_map(map_path)


def find_maps(scan_dirs: list[Path] | None = None) -> list[Path]:
    """Find all depth-0 MAP.md files."""
    if scan_dirs is None:
        scan_dirs = [PROJECT_ROOT]

    maps = []
    for d in scan_dirs:
        # Root MAP.md
        root_map = d / "MAP.md"
        if root_map.exists():
            maps.append(root_map)
        # Named *.MAP.md files directly in this dir (not sub-maps with -- separator)
        for f in sorted(d.glob("*.MAP.md")):
            if "--" not in f.stem:  # skip depth 2+ sub-maps
                maps.append(f)
        # Recursive: find *.MAP.md in subdirectories (e.g., library/*/maps/)
        for f in sorted(d.rglob("*.MAP.md")):
            if "--" not in f.stem and f not in maps:
                maps.append(f)
    return maps


def parse_map_meta(path: Path) -> dict:
    """Extract domain metadata + topic stats from a MAP.md.

    Uses the canonical `map_parser.load_map` (#256 — single parser), preserving the
    historical index behavior: skip depth>0 maps, title falls back to a title-cased
    domain, description is the first sentence of the orientation.
    """
    dm = mp_load_map(path)

    # Skip non-root maps
    if dm.depth > 0:
        return None

    # Title: the '# Heading', else a title-cased domain
    title = dm.title or dm.domain.replace("-", " ").title()

    # Description = first sentence of the orientation (up to the first '.'), with a
    # trailing '.'; fall back to the frontmatter description.
    if dm.orientation:
        first = dm.orientation.split(".", 1)[0].strip()
        description = first + "."
    else:
        description = dm.description

    total = len(dm.topics)
    # Status lives in the per-user overlay (#258), keyed by ULID node id; absent =
    # not-started. The overlay root is the map's workspace (maps dir's parent).
    status_map = _overlay_status_map(path)
    complete = sum(1 for t in dm.topics if status_map.get(t.id) == "complete")
    in_progress = sum(1 for t in dm.topics if status_map.get(t.id) == "in-progress")

    return {
        "domain": dm.domain,
        "title": title,
        "description": description,
        "total": total,
        "complete": complete,
        "in_progress": in_progress,
        "path": path,
    }


def progress_ring_svg(complete: int, total: int, size: int = 48) -> str:
    """Generate an SVG progress ring."""
    if total == 0:
        pct = 0
    else:
        pct = complete / total

    radius = (size - 6) / 2
    circumference = 2 * math.pi * radius
    filled = circumference * pct
    gap = circumference - filled
    cx = cy = size / 2

    # Color based on progress
    if pct == 0:
        color = "#6b7280"  # gray
    elif pct < 1:
        color = "#2563eb"  # blue
    else:
        color = "#16a34a"  # green

    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" class="progress-ring">
      <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="var(--border)" stroke-width="4"/>
      <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="4"
        stroke-dasharray="{filled:.1f} {gap:.1f}" stroke-linecap="round"
        transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central"
        font-size="12" font-weight="600" fill="{color}">{complete}/{total}</text>
    </svg>"""


def render_card(meta: dict) -> str:
    """Render a single domain card."""
    ring = progress_ring_svg(meta["complete"], meta["total"])

    # Map page link — find the generated map HTML relative to the index page
    # The map page is at: {workspace}/lessons/{domain}-map.html
    # The index is at: lessons/index.html (project root)
    # So link is relative from OUTPUT's parent to the map page
    map_page_path = meta["path"].parent.parent / "lessons" / f"{meta['domain']}-map.html"
    if map_page_path.exists():
        try:
            map_page = str(map_page_path.relative_to(OUTPUT.parent))
        except ValueError:
            # If they're not under a common parent, use absolute-style relative
            map_page = str(Path("..") / map_page_path.relative_to(PROJECT_ROOT))
    else:
        map_page = f"{meta['domain']}-map.html"

    status_text = []
    if meta["complete"] > 0:
        status_text.append(f'{meta["complete"]} complete')
    if meta["in_progress"] > 0:
        status_text.append(f'{meta["in_progress"]} in progress')
    remaining = meta["total"] - meta["complete"] - meta["in_progress"]
    if remaining > 0:
        status_text.append(f'{remaining} to explore')
    status = " · ".join(status_text) if status_text else f'{meta["total"]} topics to explore'

    return f"""
    <a href="{map_page}" class="domain-card">
      <div class="card-header">
        {ring}
        <h2>{meta['title']}</h2>
      </div>
      <p class="card-desc">{meta['description']}</p>
      <p class="card-status">{status}</p>
    </a>"""


def generate_page(domains: list[dict], scan_dir: Path | None = None) -> str:
    """Generate the Preact index page."""
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from lib.page_template import render_index_page

    # Parse MISSION.md if it exists
    mission = None
    mission_path = (scan_dir or PROJECT_ROOT) / "MISSION.md"
    if not mission_path.exists():
        # Try workspace
        mission_path = PROJECT_ROOT / "workspace" / "MISSION.md"
    if mission_path.exists():
        content = mission_path.read_text(encoding="utf-8")
        # Skip generic template content
        if "Tell your AI assistant" not in content and "[Your Topic]" not in content:
            # Extract title (# line)
            title_m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            # Extract Why section
            why_m = re.search(r'## Why\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
            # Extract Success Criteria (bullet list)
            criteria_m = re.search(r'## Success Criteria\n\n((?:- .+\n?)+)', content)
            criteria = []
            if criteria_m:
                criteria = [line.lstrip('- ').strip() for line in criteria_m.group(1).strip().splitlines() if line.strip()]

            mission = {
                "title": title_m.group(1).strip() if title_m else None,
                "why": why_m.group(1).strip() if why_m else None,
                "criteria": criteria[:4],  # top 4 max
            }

    # Build data island
    domain_data = []
    for d in domains:
        domain_data.append({
            "domain": d["domain"],
            "title": d["title"],
            "description": d["description"],
            "total": d["total"],
            "complete": d["complete"],
            "inProgress": d.get("in_progress", 0),
        })

    total_topics = sum(d["total"] for d in domains)
    total_complete = sum(d["complete"] for d in domains)

    data = {
        "domains": domain_data,
        "mission": mission,
        "stats": {
            "domainCount": len(domains),
            "topicCount": total_topics,
            "completeCount": total_complete,
        }
    }

    module_script = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { IndexView } from '../assets/components/IndexView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${IndexView} domains=${data.domains} stats=${data.stats} mission=${data.mission} />`,
      document.getElementById('app')
    );
"""

    css_extra = """
    body { max-width: 900px; margin: 0 auto; padding: 2rem; }
    .index-view h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
    .index-meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem; }
    .mission-fold { margin-top: 0.75rem; border-top: 1px solid var(--border); padding-top: 0.5rem; }
    .mission-fold summary { font-size: 0.8rem; color: var(--text-faint); cursor: pointer; }
    .mission-fold summary:hover { color: var(--text-muted); }
    .mission-why { font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin: 0.5rem 0; }
    .mission-criteria { padding-left: 1.2rem; margin: 0; }
    .mission-criteria li { font-size: 0.8rem; color: var(--text-muted); line-height: 1.6; }
    .domain-grid { display: flex; flex-direction: column; gap: 1rem; }
    .domain-card {
      display: block; padding: 1.25rem; background: var(--bg-elevated);
      border: 1px solid var(--border); border-radius: 10px; text-decoration: none;
      color: var(--text); transition: border-color 0.15s, box-shadow 0.15s;
    }
    .domain-card:hover { border-color: var(--accent); box-shadow: 0 2px 12px rgba(203, 166, 247, 0.1); }
    .domain-card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
    .domain-card-header h2 { font-size: 1.1rem; margin: 0; }
    .domain-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 0.5rem; }
    .domain-stat { font-size: 0.8rem; color: var(--text-faint); }
    .progress-ring { flex-shrink: 0; }
"""

    return render_index_page(
        title="All Lessons",
        body_content='<div id="app"></div>',
        data=data,
        module_script=module_script,
        css_extra=css_extra,
        depth=1,
    )

    total_topics = sum(d["total"] for d in domains)
    total_complete = sum(d["complete"] for d in domains)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Lessons — teach-me</title>
  <link rel="stylesheet" href="../assets/style.css">
  <style>
    .index-container {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 1.5rem;
    }}
    .index-header {{
      margin-bottom: 2rem;
    }}
    .index-header h1 {{
      margin-bottom: 0.25rem;
    }}
    .index-meta {{
      color: var(--text-muted);
      font-size: 0.9rem;
    }}
    .domain-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
    }}
    .domain-card {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem;
      background: var(--bg-elevated);
      text-decoration: none;
      color: inherit;
      transition: border-color 0.2s, transform 0.2s;
      display: block;
    }}
    .domain-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}
    .card-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.5rem;
    }}
    .card-header h2 {{
      font-size: 1rem;
      margin: 0;
      color: var(--text);
    }}
    .progress-ring {{
      flex-shrink: 0;
    }}
    .card-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin: 0.25rem 0;
      line-height: 1.4;
    }}
    .card-status {{
      font-size: 0.8rem;
      color: var(--text-faint, #888);
      margin: 0.5rem 0 0;
    }}
    .empty-state {{
      text-align: center;
      padding: 3rem;
      color: var(--text-muted);
    }}
    .empty-state p {{
      margin: 0.5rem 0;
    }}
    .empty-state code {{
      background: var(--code-bg);
      padding: 0.2rem 0.5rem;
      border-radius: 3px;
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>

<div class="index-container">
  <div class="index-header">
    <h1>📚 All Lessons</h1>
    <p class="index-meta">{len(domains)} domain{"s" if len(domains) != 1 else ""} · {total_topics} topics · {total_complete} complete</p>
  </div>

  <div class="domain-grid">
    {cards if cards.strip() else '''
    <div class="empty-state">
      <p>No learning domains yet.</p>
      <p>Start with: <code>kiro-cli chat "teach me about [topic]"</code></p>
    </div>'''}
  </div>
</div>

<script src="../assets/theme-toggle.js"></script>
</body>
</html>"""


def main() -> None:
    args = sys.argv[1:]

    scan_dirs = [PROJECT_ROOT]
    if "--scan-dir" in args:
        idx = args.index("--scan-dir")
        if idx + 1 < len(args):
            custom = Path(args[idx + 1])
            if not custom.is_absolute():
                custom = PROJECT_ROOT / custom
            scan_dirs = [custom]

    output = OUTPUT
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output = Path(args[idx + 1])
            if not output.is_absolute():
                output = PROJECT_ROOT / output

    maps = find_maps(scan_dirs)
    domains = []
    for m in maps:
        meta = parse_map_meta(m)
        if meta:  # skip non-root maps
            domains.append(meta)

    if not domains:
        print("No depth-0 MAP.md files found.")
        # Still generate the page with empty state
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(generate_page([], scan_dir=scan_dirs[0] if scan_dirs else None), encoding="utf-8")
        print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} (empty state)")
        return

    # Sort by title
    domains.sort(key=lambda d: d["title"])

    output.parent.mkdir(parents=True, exist_ok=True)
    page = generate_page(domains, scan_dir=scan_dirs[0] if scan_dirs else None)
    output.write_text(page, encoding="utf-8")
    print(f"✓ Generated {output.relative_to(PROJECT_ROOT)} ({len(domains)} domains)")


if __name__ == "__main__":
    main()
