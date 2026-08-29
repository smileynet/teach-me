"""Tests for map page generation — guards against regressions.

Run: python -m pytest tools/test_map_page.py -v
"""

import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_map_page import parse_map_md

# Fixture: a minimal MAP.md with dict-style leads_to
FIXTURE_MAP = """\
---
domain: test-domain
description: "Test domain for regression checks"
generated: 2026-08-12
depth: 0
parent: null
leads_to:
  - slug: next-domain
    why: "This unlocks the next thing"
  - slug: another-domain
    why: "And also this"
---

# Test Domain

## Orientation

This is a test orientation paragraph.

## Topics

### topic-one
- **title:** First Topic
- **why:** The starting point
- **prereqs:** []
- **status:** not-started

### topic-two
- **title:** Second Topic
- **why:** Builds on the first
- **prereqs:** [topic-one]
- **status:** not-started

### topic-three
- **title:** Third Topic
- **why:** The capstone
- **prereqs:** [topic-two]
- **status:** not-started
"""


def _generate_fixture_html():
    """Write fixture MAP.md to temp file, parse and generate HTML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.MAP.md', delete=False) as f:
        f.write(FIXTURE_MAP)
        f.flush()
        path = Path(f.name)

    outdir = Path(tempfile.mkdtemp())
    outfile = outdir / "test-map.html"

    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "generate_map_page.py"),
         str(path), "--output", str(outfile)],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0, f"Generation failed: {result.stderr}\n{result.stdout}"
    html = outfile.read_text()
    path.unlink()
    return html


class TestMapPageNoScopeMarkers:
    """Scope markers (○/◐/●, 'lightweight', 'substantial', 'deep') must not appear."""

    def test_no_scope_symbols_in_output(self):
        html = _generate_fixture_html()
        for marker in ['○ lightweight', '◐ substantial', '● deep']:
            assert marker not in html, f"Scope marker found: {marker}"

    def test_no_scope_text_in_data(self):
        html = _generate_fixture_html()
        assert '"scope"' not in html


class TestMapPagePreactArchitecture:
    """Page must use Preact component architecture, not vanilla JS."""

    def test_no_copy_command(self):
        html = _generate_fixture_html()
        assert 'copyCommand' not in html
        assert 'Copy command' not in html

    def test_has_import_map(self):
        html = _generate_fixture_html()
        assert 'importmap' in html
        assert 'preact' in html

    def test_imports_map_view(self):
        html = _generate_fixture_html()
        assert 'MapView' in html

    def test_has_data_island(self):
        html = _generate_fixture_html()
        assert 'id="page-data"' in html
        assert 'application/json' in html

    def test_has_dagre(self):
        html = _generate_fixture_html()
        assert 'dagre' in html

    def test_has_app_mount_point(self):
        html = _generate_fixture_html()
        assert 'id="app"' in html

    def test_uses_module_script(self):
        html = _generate_fixture_html()
        assert 'type="module"' in html


class TestMapPageDataIsland:
    """Data island must contain correct topic structure."""

    def test_topics_in_data(self):
        html = _generate_fixture_html()
        # Post-#257: the island carries the human slug plus a ULID id (not slug-as-id).
        assert '"slug": "topic-one"' in html or '"slug":"topic-one"' in html
        import re
        m = re.search(r'id="page-data">(.*?)</script>', html, re.DOTALL)
        assert m, "no page-data island"
        import json
        data = json.loads(m.group(1))
        t0 = next(t for t in data["topics"] if t["slug"] == "topic-one")
        assert len(t0["id"]) == 26, f"id not a ULID: {t0['id']!r}"

    def test_prereqs_in_data(self):
        html = _generate_fixture_html()
        import re, json
        data = json.loads(re.search(r'id="page-data">(.*?)</script>', html, re.DOTALL).group(1))
        by_slug = {t["slug"]: t for t in data["topics"]}
        # topic-two's prereq is topic-one — the island carries it as topic-one's ULID id.
        assert by_slug["topic-two"]["prereqs"] == [by_slug["topic-one"]["id"]]

    def test_leads_to_in_data(self):
        html = _generate_fixture_html()
        assert 'next-domain' in html
        assert 'This unlocks the next thing' in html
        assert 'another-domain' in html
        assert 'And also this' in html


class TestMapPageLeadsTo:
    """Leads-to data must include slug and description."""

    def test_leads_to_has_slug_and_why(self):
        html = _generate_fixture_html()
        assert 'next-domain' in html
        assert 'This unlocks the next thing' in html

    def test_no_bare_list(self):
        html = _generate_fixture_html()
        # No <li> elements — leads-to renders as buttons via component
        assert '<li>' not in html


class TestMapPageNoZoomIn:
    """No 'Zoom in' labeling — use 'Explore subtopics'."""

    def test_no_zoom_in_label(self):
        html = _generate_fixture_html()
        assert 'Zoom in' not in html
        assert '🔍' not in html


class TestMapPageStructure:
    """Basic page structure requirements."""

    def test_asset_links_relative(self):
        html = _generate_fixture_html()
        assert 'assets/style.css' in html

    def test_has_title(self):
        html = _generate_fixture_html()
        assert '<title>' in html
        assert 'Test Domain' in html

    def test_has_orientation(self):
        html = _generate_fixture_html()
        assert 'test orientation paragraph' in html

    def test_vendor_deps_relative(self):
        html = _generate_fixture_html()
        assert 'assets/vendor/preact.module.js' in html
        assert 'assets/vendor/dagre.min.js' in html


class TestMapPageOpenLesson:
    """Open lesson buttons must be clickable links, not dead buttons."""

    def test_complete_topic_has_lesson_link(self):
        """If a topic has lessonPath in data, the rendered page must have an <a> with that href."""
        html = _generate_fixture_html()
        # Our fixture has no lesson files, so no lessonPath — but verify no dead buttons
        assert 'Open lesson' not in html or 'href' in html.split('Open lesson')[0][-100:]

    def test_no_dead_open_lesson_buttons(self):
        """There must be no <button> with 'Open lesson' text — always an <a> with href."""
        html = _generate_fixture_html()
        # In a fixture with no lessons, 'Open lesson' should not appear at all
        # (status is not-started, so GenButton shows Generate, not Open)
        assert '<button' not in html or 'Open lesson' not in html
