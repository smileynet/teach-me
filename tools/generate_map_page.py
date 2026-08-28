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

# Windows consoles default to cp1252; force UTF-8 so ✓/→ glyphs don't crash.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
        # Parse leads_to list (supports both string items and dict items with slug/why)
        leads_to_section = re.search(r'^leads_to:\s*\n((?:\s+-.*\n?(?:\s+\w+:.*\n?)*)*)', fm_match.group(1), re.MULTILINE)
        leads_to = []
        if leads_to_section:
            items = re.split(r'\n\s+-\s+', '\n' + leads_to_section.group(1))
            for item in items:
                item = item.strip()
                if not item:
                    continue
                if 'slug:' in item or 'why:' in item:
                    # Dict format: parse slug and why
                    slug_m = re.search(r'slug:\s*(.+)', item)
                    why_m = re.search(r'why:\s*"?([^"]+)"?', item)
                    leads_to.append({
                        "slug": slug_m.group(1).strip() if slug_m else item.split('\n')[0].strip(),
                        "why": why_m.group(1).strip() if why_m else "",
                    })
                else:
                    # Simple string format
                    leads_to.append({"slug": item.strip(), "why": ""})
        frontmatter['leads_to'] = leads_to

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
        # Parse prereqs list (strip auto-enrichment comments)
        prereqs_str = _extract_field(block, "prereqs") or "[]"
        prereqs_str = re.sub(r'<!--.*?-->', '', prereqs_str).strip()
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
    if not LESSONS_DIR.exists():
        return None
    for f in sorted(LESSONS_DIR.glob("*.html")):
        # Skip map pages, index, and review pages
        if f.stem.endswith("-map") or f.stem == "index":
            continue
        # Direct slug match in filename
        if slug in f.stem:
            return f.name
    return None


def topic_has_reference(slug: str) -> bool:
    """Check if a reference doc exists for this topic slug."""
    ref_dir = LESSONS_DIR.parent / "reference"
    if not ref_dir.exists():
        return False
    for f in ref_dir.glob("*.html"):
        if slug in f.stem:
            return True
    return False


def topic_has_quiz(slug: str) -> bool:
    """Check if a quiz page exists for this topic slug."""
    quiz_dir = LESSONS_DIR / "quiz"
    if not quiz_dir.exists():
        return False
    for f in quiz_dir.glob("*.html"):
        if slug in f.stem:
            return True
    return False


def compute_effective_status(slug: str, map_status: str) -> str:
    """Compute topic status from actual files on disk.
    
    Status lifecycle:
      not-started → in-progress (lesson exists) → complete (lesson + reference + quiz/questions)
    
    Never downgrades: if MAP.md says 'complete', trust it (user may have marked manually).
    """
    if map_status == "complete":
        return "complete"

    has_lesson = topic_has_lesson(slug) is not None
    has_ref = topic_has_reference(slug)
    has_quiz = topic_has_quiz(slug)
    has_questions = topic_has_questions(slug) > 0

    if has_lesson and has_ref and (has_quiz or has_questions):
        return "complete"
    elif has_lesson:
        return "in-progress"
    else:
        return map_status  # keep whatever MAP.md says


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



def generate_preact_map_page(map_data: dict, output_path: Path, map_path: Path | None = None) -> str:
    """Generate a Preact-based map page from parsed MAP.md data."""
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))

    title = map_data["title"]
    orientation = map_data["orientation"]
    topics = map_data["topics"]
    leads_to = map_data["frontmatter"].get("leads_to", [])

    # Build data island
    topic_data = []
    status_updates = {}  # track changes to write back to MAP.md
    for t in topics:
        lesson_path = t.get("lesson_file") or topic_has_lesson(t["slug"])
        effective_status = compute_effective_status(t["slug"], t["status"])
        if effective_status != t["status"]:
            status_updates[t["slug"]] = effective_status
        topic_data.append({
            "id": t["slug"],
            "title": t["title"],
            "why": t["why"],
            "prereqs": t["prereqs"],
            "status": effective_status,
            "lessonPath": lesson_path or None,
        })

    # Write status updates back to MAP.md (keeps it in sync with reality)
    if status_updates and map_path and map_path.exists():
        try:
            from map_parser import update_status as _update_status
        except ImportError:
            from tools.map_parser import update_status as _update_status
        for slug, new_status in status_updates.items():
            _update_status(map_path, slug, new_status)

    # Normalize leads_to to list of dicts
    leads_to_data = []
    for lt in leads_to:
        if isinstance(lt, dict):
            leads_to_data.append({"slug": lt.get("slug", ""), "why": lt.get("why", "")})
        elif isinstance(lt, str):
            leads_to_data.append({"slug": lt, "why": ""})

    data = {
        "title": title,
        "orientation": orientation,
        "topics": topic_data,
        "leadsTo": leads_to_data,
    }

    # Determine depth from output path relative to workspace
    # lessons/ = depth 1, lessons/quiz/ = depth 2
    depth = 1
    try:
        rel = output_path.relative_to(LESSONS_DIR)
        depth = 1 + str(rel).count("/")
    except (ValueError, TypeError):
        depth = 1

    prefix = "../" * depth

    module_script = f"""
    import {{ h, render }} from 'preact';
    import htm from 'htm';
    import {{ MapView }} from '{prefix}assets/components/MapView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${{MapView}} topics=${{data.topics}} leadsTo=${{data.leadsTo}} orientation=${{data.orientation}} title=${{data.title}} />`,
      document.getElementById('app')
    );
"""

    css_extra = f"""
    body {{ max-width: none; padding: 2rem; }}
    .dag-container {{ position: relative; width: 100%; overflow-x: auto; }}
    .dag-canvas {{ position: relative; min-width: min-content; }}
    .edge-layer {{ position: absolute; top: 0; left: 0; pointer-events: none; z-index: 1; }}
    .topic-card {{
      position: absolute; width: 420px; padding: 1rem 1.2rem;
      background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px;
      z-index: 2; transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .topic-card:hover {{ border-color: var(--accent); box-shadow: 0 2px 16px rgba(203, 166, 247, 0.1); }}
    .topic-card h3 {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 0.3rem; display: flex; align-items: center; gap: 0.5rem; color: var(--text); flex-wrap: wrap; }}
    .topic-card .why {{ font-size: 0.82rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 0.5rem; }}
    .topic-card .prereq-label {{ font-size: 0.75rem; color: var(--text-faint); font-style: italic; margin-bottom: 0.5rem; }}
    .topic-card .actions {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }}
    .btn {{
      font-size: 0.75rem; padding: 0.3rem 0.6rem; border-radius: 4px;
      border: 1px solid var(--border); background: transparent; color: var(--text-muted);
      cursor: pointer; transition: border-color 0.15s, color 0.15s;
    }}
    .btn:hover {{ border-color: var(--accent); color: var(--accent); }}
    .btn.primary {{ border-color: var(--accent); color: var(--accent); }}
    .badge {{ font-size: 0.7rem; padding: 0.15rem 0.4rem; border-radius: 3px; font-weight: 500; white-space: nowrap; }}
    .badge.not-started {{ background: color-mix(in srgb, var(--text-muted) 15%, transparent); color: var(--text-muted); }}
    .badge.generating {{ background: color-mix(in srgb, var(--warning) 15%, transparent); color: var(--warning); }}
    .badge.complete {{ background: color-mix(in srgb, var(--success) 15%, transparent); color: var(--success); }}
    .badge.in-progress {{ background: color-mix(in srgb, var(--accent) 15%, transparent); color: var(--accent); }}
    .gen-progress {{ font-size: 0.75rem; color: var(--warning); margin-top: 0.4rem; font-family: monospace; }}
    .gen-stream {{ margin-top: 0.5rem; }}
    .gen-stream-header {{ font-size: 0.8rem; margin-bottom: 0.3rem; }}
    .gen-status.connecting {{ color: var(--text-muted); }}
    .gen-status.streaming {{ color: var(--warning); }}
    .gen-status.done {{ color: var(--success); }}
    .gen-status.error {{ color: var(--error); }}
    .gen-stream-output {{
      background: var(--code-bg); padding: 0.5rem; border-radius: 4px;
      font-size: 0.72rem; font-family: monospace; max-height: 150px;
      overflow-y: auto; line-height: 1.4;
    }}
    .gen-stream-output .line {{ padding: 1px 0; }}
    .gen-stream-output .phase-tool {{ color: var(--accent); }}
    .gen-stream-output .phase-writing {{ color: var(--success); }}
    .gen-modal-overlay {{
      position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
      align-items: center; justify-content: center; z-index: 1000;
    }}
    .gen-modal {{
      background: var(--bg-elevated); border: 1px solid var(--border);
      border-radius: 8px; padding: 1.5rem; max-width: 550px; width: 90%;
    }}
    .gen-modal-actions {{ display: flex; gap: 0.5rem; margin-top: 1rem; justify-content: flex-end; }}
    .leads-to {{ margin-top: 2rem; padding: 1.25rem; border-radius: 8px; background: var(--bg-elevated); border: 1px solid var(--border); }}
    .leads-to-grid {{ display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.75rem; }}
    .leads-to-btn {{
      display: flex; flex-direction: column; align-items: flex-start; padding: 0.75rem 1rem;
      border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);
      font-weight: 500; font-size: 0.95rem; cursor: pointer; text-align: left;
      transition: border-color 0.15s, background 0.15s;
    }}
    .leads-to-btn:hover {{ border-color: var(--accent); background: var(--bg-elevated); }}
    .leads-to-desc {{ font-weight: 400; font-size: 0.83rem; color: var(--text-muted); margin-top: 0.2rem; }}
    .loading {{ color: var(--text-muted); padding: 2rem; }}
    .map-header {{ margin-bottom: 1.5rem; }}
    .map-header h1 {{ font-size: 1.4rem; margin-bottom: 0.5rem; }}
    .map-header .orientation {{ color: var(--text-muted); font-size: 0.9rem; max-width: 700px; line-height: 1.5; }}
"""

    body_before = f"""<div class="map-header">
    <h1>{title}</h1>
    <p class="orientation">{orientation}</p>
  </div>"""

    from lib.page_template import render_map_page
    domain_slug = map_data["frontmatter"].get("domain", "")

    return render_map_page(
        title=title,
        domain=title,
        domain_slug=domain_slug,
        body_content=body_before + '\n  <div id="app"></div>',
        data=data,
        module_script=module_script,
        css_extra=css_extra,
        depth=depth,
    )


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
            html = generate_preact_map_page(map_data, output_path, map_path)
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

    html = generate_preact_map_page(map_data, output_path, map_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    try:
        display_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = output_path
    print(f"✓ Generated {display_path} ({len(map_data['topics'])} topics)")


if __name__ == "__main__":
    main()
