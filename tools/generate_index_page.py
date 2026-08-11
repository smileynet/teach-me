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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "lessons" / "index.html"


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
        # Named *.MAP.md files (not sub-maps with -- separator)
        for f in sorted(d.glob("*.MAP.md")):
            if "--" not in f.stem:  # skip depth 2+ sub-maps
                maps.append(f)
    return maps


def parse_map_meta(path: Path) -> dict:
    """Extract domain metadata + topic stats from a MAP.md."""
    content = path.read_text(encoding="utf-8")

    # Frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    domain = ""
    description = ""
    depth = 0
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if line.startswith("domain:"):
                domain = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("depth:"):
                try:
                    depth = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass

    # Skip non-root maps
    if depth > 0:
        return None

    # Title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else domain.replace("-", " ").title()

    # Orientation (first sentence)
    orient_match = re.search(r'## Orientation\n\n(.+?)(?:\.|$)', content)
    orientation = orient_match.group(1).strip() + "." if orient_match else description

    # Topic statuses
    statuses = re.findall(r'\*\*status:\*\*\s*(\S+)', content)
    total = len(statuses)
    complete = statuses.count("complete")
    in_progress = statuses.count("in-progress")

    return {
        "domain": domain,
        "title": title,
        "description": orientation,
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

    # Map page link (relative from lessons/index.html)
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


def generate_page(domains: list[dict]) -> str:
    """Generate the full index HTML."""
    cards = "\n".join(render_card(d) for d in domains)

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

    maps = find_maps(scan_dirs)
    domains = []
    for m in maps:
        meta = parse_map_meta(m)
        if meta:  # skip non-root maps
            domains.append(meta)

    if not domains:
        print("No depth-0 MAP.md files found.")
        # Still generate the page with empty state
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(generate_page([]), encoding="utf-8")
        print(f"✓ Generated {OUTPUT.relative_to(PROJECT_ROOT)} (empty state)")
        return

    # Sort by title
    domains.sort(key=lambda d: d["title"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page = generate_page(domains)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"✓ Generated {OUTPUT.relative_to(PROJECT_ROOT)} ({len(domains)} domains)")


if __name__ == "__main__":
    main()
