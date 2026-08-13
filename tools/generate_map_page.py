#!/usr/bin/env python3
"""Generate an interactive HTML map page from a MAP.md file.

Produces a self-contained HTML page with:
- SVG graph (Graphviz DOT) with clickable nodes
- Node coloring by state (complete/in-progress/not-started)
- Links to existing lessons or placeholder generation pages
- Breadcrumb navigation back from lessons

Usage:
    python tools/generate_map_page.py MAP.md                    # default output
    python tools/generate_map_page.py MAP.md --output map.html  # custom output
    python tools/generate_map_page.py .scratch/spike-041/data-analytics.MAP.md  # test with spike data
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = PROJECT_ROOT / "lessons"
QUESTIONS_DIR = PROJECT_ROOT / "learning-records" / "questions"

# Sub-map navigation (zoom)
try:
    from tools.map_parser import (
        find_child_map, has_child_maps, get_breadcrumb_chain,
        can_zoom_in, load_map as mp_load_map, MAX_DEPTH,
    )
except ModuleNotFoundError:
    from map_parser import (  # type: ignore[no-redef]
        find_child_map, has_child_maps, get_breadcrumb_chain,
        can_zoom_in, load_map as mp_load_map, MAX_DEPTH,
    )

# Track the maps directory for sub-map discovery
MAPS_DIR: Path | None = None


def set_workspace(workspace_path: Path) -> None:
    """Override LESSONS_DIR, QUESTIONS_DIR, and MAPS_DIR to point at a workspace."""
    global LESSONS_DIR, QUESTIONS_DIR, MAPS_DIR
    LESSONS_DIR = workspace_path / "lessons"
    QUESTIONS_DIR = workspace_path / "learning-records" / "questions"
    MAPS_DIR = workspace_path / "maps"

# State → color mapping (teach-me color vocabulary)
STATE_COLORS = {
    "complete": {"fill": "#dcfce7", "stroke": "#16a34a", "text": "#166534"},
    "in-progress": {"fill": "#dbeafe", "stroke": "#2563eb", "text": "#1e40af"},
    "not-started": {"fill": "#f3f4f6", "stroke": "#6b7280", "text": "#374151"},
}


def parse_map_md(path: Path) -> dict:
    """Parse a MAP.md file into a structured dict."""
    content = path.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    frontmatter = {}
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ':' in line and not line.strip().startswith('-'):
                key, val = line.split(':', 1)
                frontmatter[key.strip()] = val.strip().strip('"')
        # Parse leads_to list
        leads_to_match = re.findall(r'^\s+-\s+(.+)$', fm_match.group(1), re.MULTILINE)
        frontmatter['leads_to'] = leads_to_match

    # Extract orientation
    orient_match = re.search(r'## Orientation\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    orientation = orient_match.group(1).strip() if orient_match else ""

    # Extract title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else frontmatter.get('domain', 'Map')

    # Extract topics
    topics = []
    topic_blocks = re.findall(r'### (\S+)\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
    for slug, block in topic_blocks:
        topic = {"slug": slug}
        topic["title"] = _extract_field(block, "title") or slug
        topic["why"] = _extract_field(block, "why") or ""
        topic["scope"] = _extract_field(block, "scope") or "substantial"
        topic["status"] = _extract_field(block, "status") or "not-started"
        topic["lesson_file"] = _extract_field(block, "lesson_file") or ""
        # Parse prereqs list
        prereqs_str = _extract_field(block, "prereqs") or "[]"
        topic["prereqs"] = [p.strip() for p in prereqs_str.strip("[]").split(",") if p.strip()]
        topics.append(topic)

    return {
        "frontmatter": frontmatter,
        "title": title,
        "orientation": orientation,
        "topics": topics,
    }


def _extract_field(block: str, field: str) -> str | None:
    match = re.search(rf'\*\*{field}:\*\*\s*(.+)', block)
    return match.group(1).strip() if match else None


def topic_has_lesson(slug: str) -> str | None:
    """Find the lesson file for a topic slug. Returns relative path or None.
    
    Matches by: slug in filename, or slug appears in file content (lesson-id, heading).
    """
    for f in sorted(LESSONS_DIR.glob("*.html")):
        # Skip map pages, index, and review pages
        if f.stem.endswith("-map") or f.stem == "index":
            continue
        # Direct slug match in filename
        if slug in f.stem:
            return f.name
    return None


def topic_has_questions(slug: str) -> int:
    """Count quick-check questions for a topic slug. Checks all JSONL files for matching tags/lesson_id."""
    import json
    count = 0
    for f in QUESTIONS_DIR.glob("*.jsonl"):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
                if card.get("question_type") == "quick-check" and (
                    slug in card.get("tags", []) or slug in card.get("lesson_id", "")
                ):
                    count += 1
            except json.JSONDecodeError:
                continue
    return count


def generate_dot(map_data: dict) -> str:
    """Generate Graphviz DOT from parsed map data."""
    topics = map_data["topics"]
    lines = [
        'digraph G {',
        '  rankdir=TB;',
        '  node [shape=box, style="filled,rounded", fontname="system-ui, sans-serif", fontsize=12, margin="0.3,0.2"];',
        '  edge [color="#6b7280", arrowsize=0.7];',
        '  bgcolor="transparent";',
        '',
    ]

    for topic in topics:
        # Determine effective status (if lesson exists but status says not-started, show in-progress)
        lesson_path = topic.get("lesson_file") or topic_has_lesson(topic["slug"])
        effective_status = topic["status"]
        if lesson_path and effective_status == "not-started":
            effective_status = "in-progress"
        colors = STATE_COLORS.get(effective_status, STATE_COLORS["not-started"])

        # URL: always scroll to topic card on the map page
        url = f"#topic-{topic['slug']}"

        label = topic["title"]

        # Escape quotes for DOT syntax
        safe_label = label.replace('"', '\\"')
        safe_why = topic["why"].replace('"', '\\"')

        lines.append(
            f'  "{topic["slug"]}" ['
            f'label="{safe_label}", '
            f'fillcolor="{colors["fill"]}", '
            f'color="{colors["stroke"]}", '
            f'fontcolor="{colors["text"]}", '
            f'URL="{url}", '
            f'tooltip="{safe_why}"'
            f'];'
        )

    # Edges from prereqs
    for topic in topics:
        for prereq in topic["prereqs"]:
            lines.append(f'  "{prereq}" -> "{topic["slug"]}";')

    lines.append('}')
    return '\n'.join(lines)


def render_svg(dot_source: str) -> str:
    """Render DOT to SVG via Graphviz."""
    result = subprocess.run(
        ['dot', '-Tsvg'],
        input=dot_source, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Graphviz error: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    svg = result.stdout
    # Remove XML declaration and DOCTYPE
    svg = re.sub(r'<\?xml[^>]*\?>\n?', '', svg)
    svg = re.sub(r'<!DOCTYPE[^>]*>\n?', '', svg)
    # Remove fixed width/height, keep viewBox for responsive
    svg = re.sub(r'\s*width="\d+pt"', '', svg)
    svg = re.sub(r'\s*height="\d+pt"', '', svg)
    # Add responsive class
    svg = svg.replace('<svg ', '<svg class="map-graph" ', 1)
    # Handle Graphviz output where <svg has a newline before attributes
    if 'class="map-graph"' not in svg:
        svg = svg.replace('<svg\n', '<svg class="map-graph"\n', 1)
    return svg


def _find_map_file_for_data(maps_dir: Path, map_data: dict) -> Path:
    """Find the MAP.md file matching parsed map_data by domain."""
    domain = map_data["frontmatter"].get("domain", "")
    for f in maps_dir.glob("*.MAP.md"):
        if domain in f.stem or f.stem.replace(".MAP", "") == domain:
            return f
    raise FileNotFoundError(f"No MAP.md found for domain '{domain}' in {maps_dir}")


def generate_page(map_data: dict, svg: str, index_link: str = "index.html", maps_dir: Path | None = None, output_path: Path | None = None) -> str:
    """Generate the full HTML page."""
    title = map_data["title"]
    orientation = map_data["orientation"]
    topics = map_data["topics"]
    leads_to = map_data["frontmatter"].get("leads_to", [])
    depth = int(map_data["frontmatter"].get("depth", 0))
    parent_domain = map_data["frontmatter"].get("parent")

    # Detect child maps for zoom-in affordances
    child_maps: dict[str, Path] = {}
    if maps_dir and maps_dir.is_dir():
        try:
            dm = mp_load_map(maps_dir / _find_map_file_for_data(maps_dir, map_data))
            child_maps = has_child_maps(maps_dir, dm)
        except (FileNotFoundError, ValueError):
            # Fall back to slug-based detection
            for t in topics:
                child = find_child_map(maps_dir, t["slug"])
                if child:
                    child_maps[t["slug"]] = child

    # Breadcrumb navigation (only for depth > 0)
    breadcrumb_html = ""
    if depth > 0 and parent_domain:
        # Build breadcrumb: link to parent map page
        parent_map_page = f"{parent_domain}-map.html"
        breadcrumb_html = f"""
  <nav class="breadcrumb" aria-label="Map navigation">
    <a href="{parent_map_page}">← {parent_domain.replace('-', ' ').title()}</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-current">{title}</span>
  </nav>"""

    # Build topic cards for the sidebar/details
    topic_cards = []
    for t in topics:
        # Find lesson: explicit lesson_file field, or slug-based detection
        lesson_path = t.get("lesson_file") or topic_has_lesson(t["slug"])
        status_badge = {
            "complete": '<span class="badge complete">✓ complete</span>',
            "in-progress": '<span class="badge in-progress">◐ in progress</span>',
            "not-started": '<span class="badge not-started">○ not started</span>',
        }.get(t["status"], "")

        if lesson_path:
            action = f'<a href="{lesson_path}" class="topic-link">Open lesson →</a>'
        else:
            action = f'<button class="generate-btn" onclick="offerGenerate(\'{t["slug"]}\', \'{t["title"]}\')">Generate this topic</button>'

        # Quiz link
        q_count = topic_has_questions(t["slug"])
        if q_count > 0:
            quiz_action = f'<a href="review/quick-check.html" class="topic-link quiz-link">Quiz ({q_count}) →</a>'
        else:
            quiz_action = f'<button class="generate-btn quiz-gen" onclick="offerGenerateQuiz(\'{t["slug"]}\', \'{t["title"]}\')">Generate quiz</button>'

        # Prereqs display
        prereqs_text = f'After: {", ".join(t["prereqs"])}' if t["prereqs"] else "Start here"

        topic_cards.append(f"""
    <div class="topic-card" id="topic-{t['slug']}">
      <h3>{t['title']} {status_badge}</h3>
      <p class="topic-why">{t['why']}</p>
      <p class="topic-prereqs">{prereqs_text}</p>
      <div class="topic-actions">{action} {quiz_action}</div>
    </div>""")

    # Leads-to section
    leads_html = ""
    if leads_to:
        items = ""
        for lt in leads_to:
            # Handle both dict format and string format
            if isinstance(lt, dict):
                label = lt.get("slug", lt.get("why", "")).replace("-", " ").title()
            elif isinstance(lt, str):
                # Strip "slug: " prefix if present (parse_map_md artifact)
                label = lt.replace("slug: ", "").replace("-", " ").title()
            else:
                label = str(lt).replace("-", " ").title()
            items += f"<li>{label}</li>"
        leads_html = f"""
    <div class="leads-to">
      <h2>🚀 Where This Leads</h2>
      <p>After exploring this domain, these become accessible:</p>
      <ul>{items}</ul>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Map: {title}</title>
  <link rel="stylesheet" href="../assets/style.css">
  <style>
    html {{ scroll-behavior: smooth; }}
    .lesson-nav {{
      padding: 0.5rem 0;
      margin-bottom: 0.5rem;
      border-bottom: 1px solid var(--border);
      font-size: 0.85rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .lesson-nav a {{
      color: var(--link);
      text-decoration: none;
    }}
    .lesson-nav a:hover {{ text-decoration: underline; }}
    .lesson-nav .nav-position {{
      color: var(--text-muted);
    }}
    .map-container {{
      display: flex;
      flex-direction: column;
      gap: 2rem;
      max-width: 900px;
      margin: 0 auto;
      padding: 1rem;
    }}
    .map-graph {{
      max-width: 100%;
      height: auto;
      cursor: pointer;
    }}
    .map-graph a:hover polygon,
    .map-graph a:hover path {{
      filter: brightness(0.9);
    }}
    .orientation {{
      font-size: 1rem;
      color: var(--text-muted);
      line-height: 1.6;
      border-left: 4px solid var(--accent);
      padding-left: 1rem;
    }}
    .topic-card {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin: 0.75rem 0;
      background: var(--bg-elevated);
      scroll-margin-top: 1rem;
      transition: border-color 0.4s ease, box-shadow 0.4s ease;
    }}
    .topic-card:target {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 25%, transparent);
    }}
    .topic-card h3 {{
      margin: 0 0 0.25rem 0;
      font-size: 1rem;
    }}
    .topic-why {{
      color: var(--text-muted);
      font-size: 0.9rem;
      margin: 0.25rem 0;
    }}
    .topic-prereqs {{
      font-size: 0.8rem;
      color: var(--text-faint, #888);
    }}
    .badge {{
      font-size: 0.7rem;
      padding: 0.1rem 0.4rem;
      border-radius: 3px;
      font-weight: 600;
    }}
    .badge.complete {{ background: #dcfce7; color: #166534; }}
    .badge.in-progress {{ background: #dbeafe; color: #1e40af; }}
    .badge.not-started {{ background: #f3f4f6; color: #6b7280; }}
    .topic-link {{
      display: inline-block;
      margin-top: 0.5rem;
      color: var(--link);
      font-size: 0.9rem;
    }}
    .topic-actions {{
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-top: 0.5rem;
      flex-wrap: wrap;
    }}
    .quiz-link {{
      color: var(--success, #16a34a);
    }}
    .quiz-gen {{
      border-color: var(--success, #16a34a);
      color: var(--success, #16a34a);
    }}
    .generate-btn {{
      margin-top: 0.5rem;
      padding: 0.4rem 0.8rem;
      border: 1px solid var(--accent);
      border-radius: 4px;
      background: var(--bg-surface);
      color: var(--accent);
      cursor: pointer;
      font-size: 0.85rem;
    }}
    .generate-btn:hover {{ background: var(--bg-elevated); }}
    .breadcrumb {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin: 0.5rem 0 0.25rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .breadcrumb a {{
      color: var(--link);
      text-decoration: none;
      font-weight: 500;
    }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    .breadcrumb-sep {{ color: var(--text-faint, #999); }}
    .breadcrumb-current {{ font-weight: 500; }}
      font-style: italic;
    }}
    .leads-to {{
      margin-top: 2rem;
      padding: 1.25rem;
      border-radius: 8px;
      background: var(--bg-elevated);
      border: 1px solid var(--border);
    }}
    .leads-to ul {{
      padding-left: 1.5rem;
      margin: 0.5rem 0 0;
    }}
    .leads-to li {{
      color: var(--text-muted);
      margin: 0.25rem 0;
    }}
    .legend {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .legend-swatch {{
      width: 14px;
      height: 14px;
      border-radius: 3px;
      border: 1px solid;
    }}
    .modal-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      z-index: 100;
      align-items: center;
      justify-content: center;
    }}
    .modal-overlay.show {{ display: flex; }}
    .modal {{
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      max-width: 500px;
      width: 90%;
    }}
    .modal h3 {{ margin-top: 0; }}
    .modal pre {{
      background: var(--code-bg);
      padding: 0.75rem;
      border-radius: 4px;
      font-size: 0.8rem;
      overflow-x: auto;
    }}
    .modal-actions {{
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
    }}
    .modal-actions button {{
      padding: 0.4rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      border: 1px solid var(--border);
      font-size: 0.85rem;
    }}
    .modal-actions .primary {{
      background: var(--accent);
      color: var(--bg);
      border-color: var(--accent);
    }}
  </style>
</head>
<body>

<div class="map-container">
  <nav class="lesson-nav">
    <a href="{index_link}" class="back-to-map">← All Lessons</a>
    <span class="nav-position">{len(map_data['topics'])} topics · {sum(1 for t in map_data['topics'] if t['status'] == 'complete')} complete</span>
  </nav>
  {breadcrumb_html}
  <h1>🗺️ {title}</h1>
  <p class="orientation">{orientation}</p>

  <div class="legend">
    <span class="legend-item"><span class="legend-swatch" style="background:#dcfce7;border-color:#16a34a"></span> Complete</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#dbeafe;border-color:#2563eb"></span> In progress</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#f3f4f6;border-color:#6b7280"></span> Not started</span>
  </div>

  {svg}

  <h2>Topics</h2>
  {"".join(topic_cards)}

  {leads_html}
</div>

<!-- Generation modal -->
<div class="modal-overlay" id="gen-modal">
  <div class="modal">
    <h3 id="gen-title">Generate topic</h3>
    <p id="gen-desc">This topic hasn't been created yet. Generate it with:</p>
    <pre id="gen-command"></pre>
    <div class="modal-actions">
      <button onclick="copyCommand()">📋 Copy command</button>
      <button onclick="closeModal()">Close</button>
    </div>
  </div>
</div>

<script>
function offerGenerate(slug, title) {{
  document.getElementById('gen-title').textContent = 'Generate: ' + title;
  document.getElementById('gen-command').textContent = 'kiro-cli chat "teach me about ' + title + '"';
  document.getElementById('gen-modal').classList.add('show');
}}

function offerGenerateQuiz(slug, title) {{
  document.getElementById('gen-title').textContent = 'Generate Quiz: ' + title;
  document.getElementById('gen-command').textContent = 'kiro-cli chat "generate quick-check questions for ' + title + '"';
  document.getElementById('gen-modal').classList.add('show');
}}

function closeModal() {{
  document.getElementById('gen-modal').classList.remove('show');
}}

function copyCommand() {{
  const cmd = document.getElementById('gen-command').textContent;
  navigator.clipboard.writeText(cmd).then(() => {{
    document.querySelector('.modal-actions .primary')
  }});
}}

// Close modal on overlay click
document.getElementById('gen-modal').addEventListener('click', function(e) {{
  if (e.target === this) closeModal();
}});
</script>
<script src="../assets/theme-toggle.js"></script>

</body>
</html>"""


def find_all_maps() -> list[Path]:
    """Auto-discover depth-0 MAP.md files in the project."""
    maps = []
    # Root MAP.md
    root = PROJECT_ROOT / "MAP.md"
    if root.exists():
        maps.append(root)
    # Named *.MAP.md at root (not sub-maps with --)
    for f in sorted(PROJECT_ROOT.glob("*.MAP.md")):
        if "--" not in f.stem:
            maps.append(f)
    return maps


def main() -> None:
    args = sys.argv[1:]

    # Handle --workspace flag (repoints lessons/questions directories)
    if "--workspace" in args:
        idx = args.index("--workspace")
        if idx + 1 < len(args):
            ws = Path(args[idx + 1])
            if not ws.is_absolute():
                ws = PROJECT_ROOT / ws
            set_workspace(ws)
            args = args[:idx] + args[idx + 2:]  # remove flag from args

    # Auto-discover mode: no args = generate all maps
    if not args or args == []:
        maps = find_all_maps()
        if not maps:
            print("No MAP.md files found at project root. Pass a path explicitly.")
            sys.exit(0)
        for map_path in maps:
            map_data = parse_map_md(map_path)
            domain = map_data["frontmatter"].get("domain", map_path.stem)
            output_path = PROJECT_ROOT / "lessons" / f"{domain}-map.html"
            dot = generate_dot(map_data)
            svg = render_svg(dot)
            index_path = PROJECT_ROOT / "lessons" / "index.html"
            try:
                index_link = str(Path(os.path.relpath(index_path, output_path.parent)))
            except ValueError:
                index_link = "index.html"
            html = generate_page(map_data, svg, index_link, maps_dir=map_path.parent)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            try:
                display_path = output_path.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = output_path
            print(f"✓ Generated {display_path} ({len(map_data['topics'])} topics)")
        return

    # Explicit path mode
    map_path = Path(args[0])
    if not map_path.is_absolute():
        map_path = PROJECT_ROOT / map_path

    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1])
            if not output_path.is_absolute():
                output_path = PROJECT_ROOT / output_path

    if not map_path.exists():
        print(f"MAP.md not found: {map_path}")
        sys.exit(1)

    map_data = parse_map_md(map_path)
    domain = map_data["frontmatter"].get("domain", map_path.stem)

    if output_path is None:
        output_path = PROJECT_ROOT / "lessons" / f"{domain}-map.html"

    dot = generate_dot(map_data)
    svg = render_svg(dot)
    index_path = PROJECT_ROOT / "lessons" / "index.html"
    try:
        index_link = str(Path(os.path.relpath(index_path, output_path.parent)))
    except ValueError:
        index_link = "index.html"
    maps_dir_resolved = MAPS_DIR or map_path.parent
    html = generate_page(map_data, svg, index_link, maps_dir=maps_dir_resolved)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    try:
        display_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = output_path
    print(f"✓ Generated {display_path} ({len(map_data['topics'])} topics)")


if __name__ == "__main__":
    main()
