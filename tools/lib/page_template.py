"""page_template.py — THE single source of truth for all page HTML shells.

Generators call these functions with content data; templates handle all boilerplate.
Adding a new global script, stylesheet, or component = edit this file once.

Usage:
    from tools.lib.page_template import render_lesson_page, render_reference_page, ...

    html = render_lesson_page(
        title="Blender NPR Shader Fundamentals",
        lesson_number=2,
        domain="Blender → Godot Shader Pipeline",
        domain_slug="blender-godot-shaders",
        lesson_id="0002-blender-npr-shaders",
        reading_time=12,
        win="You can build a basic toon material...",
        body_content=content_html,
        glossary_data={"shader-to-rgb": "...", "npr": "..."},
    )
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMPORT_MAP_PATH = PROJECT_ROOT / "assets" / "import-map.json"


# --- Import map ---

def _import_map(depth: int) -> str:
    """Load and adjust import map paths for the page's directory depth."""
    raw = json.loads(IMPORT_MAP_PATH.read_text())
    prefix = "../" * depth
    adjusted = {}
    for key, val in raw["imports"].items():
        if val.startswith("./"):
            adjusted[key] = prefix + val[2:]
        else:
            adjusted[key] = val
    return json.dumps({"imports": adjusted}, indent=4)


# --- Breadcrumb navigation ---

def _breadcrumb(crumbs: list[tuple[str, str | None]]) -> str:
    """Render breadcrumb nav from list of (label, url|None) tuples.

    Last item (url=None) is the current page — rendered as plain text.
    """
    if not crumbs:
        return ""
    parts = []
    for label, url in crumbs:
        if url:
            parts.append(f'<a href="{url}">{_esc(label)}</a>')
        else:
            parts.append(f"<span>{_esc(label)}</span>")
    inner = ' <span class="nav-sep">›</span> '.join(parts)
    return f'<nav class="page-nav" aria-label="Breadcrumb">{inner}</nav>\n'


def _esc(s: str) -> str:
    """Minimal HTML escaping for text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# --- Base page ---

def _base_page(
    *,
    title: str,
    depth: int = 1,
    body_content: str,
    breadcrumb_html: str = "",
    head_extras: str = "",
    data_islands: dict[str, Any] | None = None,
    include_glossary_css: bool = False,
    include_page_shell: bool = True,
    include_dagre: bool = False,
    module_script: str = "",
    css_extra: str = "",
    lesson_actions: dict[str, str] | None = None,
) -> str:
    """Render a complete HTML page with all boilerplate.

    This is the single function that emits DOCTYPE through </html>.
    All page-type renderers call this.
    """
    prefix = "../" * depth
    import_map = _import_map(depth)

    # Head: blocking prefs script + stylesheets
    prefs_script = f'  <script src="{prefix}assets/typography-prefs.js"></script>\n'
    style_link = f'  <link rel="stylesheet" href="{prefix}assets/style.css">\n'
    glossary_css = f'  <link rel="stylesheet" href="{prefix}assets/glossary.css">\n' if include_glossary_css else ""
    dagre_script = f'  <script src="{prefix}assets/vendor/dagre.min.js"></script>\n' if include_dagre else ""

    style_block = ""
    if css_extra:
        style_block = f"  <style>\n{css_extra}\n  </style>\n"

    # Data islands
    islands_html = ""
    if data_islands:
        for island_id, island_data in data_islands.items():
            data_json = json.dumps(island_data, ensure_ascii=False)
            islands_html += f'<script type="application/json" id="{island_id}">{data_json}</script>\n'

    # Lesson-actions config: LessonActions.js reads these data-* attrs (queried via
    # script[data-domain]) to build /api/map/{domain}/{slug}/status. Emitted BEFORE
    # page-shell.js so the attributes exist when mountLessonActions() runs.
    lesson_actions_script = ""
    if lesson_actions:
        attrs = " ".join(
            f'data-{k}="{_esc(str(v))}"' for k, v in lesson_actions.items()
        )
        lesson_actions_script = f'<script type="application/json" id="lesson-actions-config" {attrs}></script>\n'

    # Page shell or custom module script
    shell_script = ""
    if include_page_shell:
        shell_script = f'<script type="module" src="{prefix}assets/page-shell.js"></script>\n'
    if module_script:
        shell_script += f"<script type=\"module\">\n{module_script}\n</script>\n"

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_esc(title)}</title>
{prefs_script}{style_link}{glossary_css}{style_block}{head_extras}  <script type="importmap">
{import_map}
  </script>
{dagre_script}</head>
<body>

{breadcrumb_html}{body_content}

{islands_html}{lesson_actions_script}{shell_script}
</body>
</html>"""


# --- Lesson page ---

def render_lesson_page(
    *,
    title: str,
    lesson_number: int,
    domain: str,
    domain_slug: str,
    lesson_id: str,
    reading_time: int,
    win: str,
    body_content: str,
    glossary_data: dict[str, str] | None = None,
    key_concept: str = "",
    depth: int = 1,
) -> str:
    """Render a complete lesson page.

    Args:
        body_content: The lesson body (h2 sections, paragraphs, SVGs, tables).
                      Does NOT include h1, lesson-meta, or key-concept — those
                      are generated from structured data.
    """
    # Breadcrumb: All Lessons › Domain › Title
    map_page = f"{domain_slug}-map.html"
    crumbs = [
        ("All Lessons", "index.html"),
        (domain, map_page),
        (title, None),
    ]

    # Lesson meta block
    meta_html = f"""<h1>{_esc(title)}</h1>

<div class="lesson-meta">
  Lesson {lesson_number} · {_esc(domain)} · ~{reading_time} min read<br>
  <strong>Win:</strong> {_esc(win)}
</div>
"""

    # Key concept block
    concept_html = ""
    if key_concept:
        concept_html = f"""<div class="key-concept">
  <strong>After this lesson:</strong> {key_concept}
</div>
"""

    full_body = meta_html + concept_html + body_content

    # Data islands
    islands = {}
    if glossary_data:
        islands["glossary-data"] = glossary_data

    return _base_page(
        title=f"Lesson {lesson_number}: {title}",
        depth=depth,
        body_content=full_body,
        breadcrumb_html=_breadcrumb(crumbs),
        data_islands=islands if islands else None,
        include_glossary_css=bool(glossary_data),
        include_page_shell=True,
        lesson_actions={
            "domain": domain_slug,
            "lesson-id": lesson_id,
            "map-page": map_page,
            "topic-title": title,
        },
    )


# --- Reference page ---

def render_reference_page(
    *,
    title: str,
    domain: str,
    domain_slug: str,
    lesson_id: str,
    body_content: str,
    depth: int = 1,
) -> str:
    """Render a complete reference page."""
    map_page = f"{'../' * depth}lessons/{domain_slug}-map.html"
    lesson_page = f"{'../' * depth}lessons/{lesson_id}.html"

    crumbs = [
        ("All Lessons", f"{'../' * depth}lessons/index.html"),
        (domain, map_page),
        (title, lesson_page),
        ("Reference", None),
    ]

    header = f"""<h1>{_esc(title)} — Quick Reference</h1>

<div class="lesson-meta">
  Reference · {_esc(domain)}<br>
  Pull this up when you need a quick lookup.
</div>
"""

    return _base_page(
        title=f"Reference: {title}",
        depth=depth,
        body_content=header + body_content,
        breadcrumb_html=_breadcrumb(crumbs),
        include_page_shell=True,
    )


# --- Quiz page ---

def render_quiz_page(
    *,
    title: str,
    questions: list[dict],
    lesson_id: str,
    lesson_file: str,
    map_page: str,
    domain: str = "",
    domain_slug: str = "",
    depth: int = 2,
) -> str:
    """Render a complete quiz page."""
    # The quiz always sits one directory below its lesson (lessons/quiz/ or
    # lessons/{domain}/quiz/), so the lesson is always one level up.
    lesson_url = f"../{lesson_id}.html"
    # index.html and the domain map live at the lessons/ root. The quiz is
    # `depth - 1` levels below lessons/ (depth 2 → 1 level, depth 3 → 2 levels).
    up_to_lessons = "../" * (depth - 1)
    # assets/ lives at the workspace root, i.e. `depth` levels up from the quiz.
    assets_prefix = "../" * depth

    crumbs_list: list[tuple[str, str | None]] = []
    if domain:
        index_url = f"{up_to_lessons}index.html"
        map_url = f"{up_to_lessons}{domain_slug}-map.html"
        crumbs_list = [
            ("All Lessons", index_url),
            (domain, map_url),
            (title, lesson_url),
            ("Quiz", None),
        ]
    else:
        crumbs_list = [
            (title, lesson_url),
            ("Quiz", None),
        ]

    page_data = {
        "questions": questions,
        "title": title,
        "lessonFile": lesson_file,
        "mapPage": map_page,
    }

    module = f"""\
    import {{ h, render }} from 'preact';
    import htm from 'htm';
    import {{ QuizView }} from '{assets_prefix}assets/components/QuizView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${{QuizView}} questions=${{data.questions}} title=${{data.title}} />`,
      document.getElementById('app')
    );"""

    body = '  <div id="app"></div>'

    return _base_page(
        title=f"Quiz: {title}",
        depth=depth,
        body_content=body,
        breadcrumb_html=_breadcrumb(crumbs_list),
        data_islands={"page-data": page_data},
        include_page_shell=True,
        module_script=module,
    )


# --- Map page ---

def render_map_page(
    *,
    title: str,
    domain: str,
    domain_slug: str,
    body_content: str,
    data: dict | list | None = None,
    module_script: str = "",
    css_extra: str = "",
    depth: int = 1,
) -> str:
    """Render a complete map page."""
    crumbs = [
        ("All Lessons", "index.html"),
        (domain, None),
    ]

    return _base_page(
        title=f"Map: {title}",
        depth=depth,
        body_content=body_content,
        breadcrumb_html=_breadcrumb(crumbs),
        data_islands={"page-data": data} if data else None,
        include_page_shell=False,
        include_dagre=True,
        module_script=module_script,
        css_extra=css_extra,
    )


# --- Index page ---

def render_index_page(
    *,
    title: str = "All Lessons",
    body_content: str = "",
    data: dict | list | None = None,
    module_script: str = "",
    css_extra: str = "",
    depth: int = 1,
) -> str:
    """Render the All Lessons index page (root — no breadcrumb)."""
    return _base_page(
        title=f"{title} — teach-me",
        depth=depth,
        body_content=body_content,
        data_islands={"page-data": data} if data else None,
        include_page_shell=False,
        module_script=module_script,
        css_extra=css_extra,
    )


# --- Resources page ---

def render_resources_page(
    *,
    title: str = "Resources",
    domain: str,
    domain_slug: str,
    body_content: str,
    data: dict | list | None = None,
    module_script: str = "",
    css_extra: str = "",
    depth: int = 1,
) -> str:
    """Render a resources/further reading page."""
    crumbs: list[tuple[str, str | None]] = [("All Lessons", "index.html")]
    if domain_slug:
        crumbs.append((domain, f"{domain_slug}-map.html"))
    crumbs.append(("Resources", None))

    return _base_page(
        title=f"Resources: {domain}",
        depth=depth,
        body_content=body_content,
        breadcrumb_html=_breadcrumb(crumbs),
        data_islands={"page-data": data} if data else None,
        include_page_shell=False,
        module_script=module_script,
        css_extra=css_extra,
    )
