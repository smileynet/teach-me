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

    map_data = parse_map_md(path)
    # generate_map_html needs the parsed data — call the full pipeline
    # We'll generate to a temp dir
    outdir = Path(tempfile.mkdtemp())
    outfile = outdir / "test-map.html"

    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "generate_map_page.py"),
         str(path), "--output", str(outfile)],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0, f"Generation failed: {result.stderr}"
    html = outfile.read_text()
    path.unlink()
    return html


class TestMapPageNoScopeMarkers:
    """Scope markers (○/◐/●, 'lightweight', 'substantial', 'deep') must not appear."""

    def test_no_scope_symbols_in_output(self):
        html = _generate_fixture_html()
        for marker in ['○ lightweight', '◐ substantial', '● deep']:
            assert marker not in html, f"Scope marker found: {marker}"

    def test_no_scope_text_in_topic_cards(self):
        html = _generate_fixture_html()
        assert 'Scope:' not in html


class TestMapPageLiveGeneration:
    """Generation must use SSE, not copy-command."""

    def test_no_copy_command(self):
        html = _generate_fixture_html()
        assert 'copyCommand' not in html
        assert 'Copy command' not in html
        assert '📋' not in html

    def test_has_event_source(self):
        html = _generate_fixture_html()
        assert 'EventSource' in html

    def test_hits_api_generate(self):
        html = _generate_fixture_html()
        assert '/api/generate' in html

    def test_has_live_output_element(self):
        html = _generate_fixture_html()
        assert 'id="gen-output"' in html

    def test_has_cancel_button(self):
        html = _generate_fixture_html()
        assert 'cancelGeneration' in html


class TestMapPageLeadsTo:
    """Leads-to section must render as buttons with descriptions."""

    def test_leads_to_are_buttons(self):
        html = _generate_fixture_html()
        assert 'leads-to-btn' in html

    def test_leads_to_has_descriptions(self):
        html = _generate_fixture_html()
        assert 'leads-to-desc' in html
        assert 'This unlocks the next thing' in html
        assert 'And also this' in html

    def test_no_bare_list(self):
        html = _generate_fixture_html()
        # Should not have <li> in leads-to section
        # (buttons replace the old <ul><li> pattern)
        assert '<li>' not in html.split('Where This Leads')[1] if 'Where This Leads' in html else True


class TestMapPageSubtopics:
    """Explore subtopics button must exist with clear labeling."""

    def test_has_explore_subtopics(self):
        html = _generate_fixture_html()
        assert 'Explore subtopics' in html

    def test_no_zoom_in_label(self):
        html = _generate_fixture_html()
        assert 'Zoom in' not in html
        assert '🔍' not in html

    def test_subtopic_has_tooltip(self):
        html = _generate_fixture_html()
        assert 'Break this topic into' in html


class TestMapPageSequentialFlow:
    """Topics should show sequential prereqs clearly."""

    def test_start_here_for_first_topic(self):
        html = _generate_fixture_html()
        assert 'Start here' in html

    def test_after_label_for_subsequent(self):
        html = _generate_fixture_html()
        assert 'After: topic-one' in html
        assert 'After: topic-two' in html


class TestMapPageFullURLs:
    """Links must be relative paths (full URLs are the server's job, 
    but internal links must be valid relative paths)."""

    def test_asset_links_relative(self):
        html = _generate_fixture_html()
        assert 'href="../assets/style.css"' in html

    def test_lesson_actions_included(self):
        html = _generate_fixture_html()
        # Map pages may or may not include lesson-actions.js
        # but must include theme-toggle
        assert 'theme-toggle' in html
