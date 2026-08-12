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

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = PROJECT_ROOT / "lessons"
QUESTIONS_DIR = PROJECT_ROOT / "learning-records" / "questions"

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
        # Add scope indicator
        scope_icon = {"lightweight": "○", "substantial": "◐", "deep": "●"}.get(topic["scope"], "◐")

        # Escape quotes for DOT syntax
        safe_label = label.replace('"', '\\"')
        safe_why = topic["why"].replace('"', '\\"')

        lines.append(
            f'  "{topic["slug"]}" ['
            f'label="{safe_label}\\n{scope_icon} {topic["scope"]}", '
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
    return svg


def generate_page(map_data: dict, svg: str) -> str:
    """Generate the full HTML page."""
    title = map_data["title"]
    orientation = map_data["orientation"]
    topics = map_data["topics"]
    leads_to = map_data["frontmatter"].get("leads_to", [])

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

        topic_cards.append(f"""
    <div class="topic-card" id="topic-{t['slug']}">
      <h3>{t['title']} {status_badge}</h3>
      <p class="topic-why">{t['why']}</p>
      <p class="topic-scope">Scope: {t['scope']} · Prereqs: {', '.join(t['prereqs']) or 'none'}</p>
      <div class="topic-actions">{action} {quiz_action}</div>
    </div>""")

    # Leads-to section
    leads_html = ""
    if leads_to:
        items = "".join(f"<li>{lt.replace('-', ' ').title()}</li>" for lt in leads_to)
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
    .topic-scope {{
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
    <a href="index.html" class="back-to-map">← All Lessons</a>
    <span class="nav-position">{len(map_data['topics'])} topics · {sum(1 for t in map_data['topics'] if t['status'] == 'complete')} complete</span>
  </nav>
  <h1>🗺️ {title}</h1>
  <p class="orientation">{orientation}</p>

  <div class="legend">
    <span class="legend-item"><span class="legend-swatch" style="background:#dcfce7;border-color:#16a34a"></span> Complete</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#dbeafe;border-color:#2563eb"></span> In progress</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#f3f4f6;border-color:#6b7280"></span> Not started</span>
    <span class="legend-item">○ lightweight · ◐ substantial · ● deep</span>
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


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: python tools/generate_map_page.py <MAP.md> [--output <path>]")
        sys.exit(1)

    map_path = Path(args[0])
    if not map_path.is_absolute():
        map_path = PROJECT_ROOT / map_path

    output_path = PROJECT_ROOT / "lessons" / "map.html"
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
    dot = generate_dot(map_data)
    svg = render_svg(dot)
    html = generate_page(map_data, svg)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✓ Generated {output_path.relative_to(PROJECT_ROOT)} ({len(map_data['topics'])} topics)")


if __name__ == "__main__":
    main()
