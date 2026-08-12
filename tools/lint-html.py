#!/usr/bin/env python3
"""
Lint lesson and map HTML pages for required structure.

Checks filename-based rules:
- Lesson pages (NNNN-*.html): require style.css, lesson-actions.js, theme-toggle.js, <h1>, glossary-data
- Map pages (*-map.html): require style.css, theme-toggle.js, map-graph SVG, gen-modal
- Index page: require style.css, theme-toggle.js
- Spike pages: skip (test fixtures, not user-facing)

Usage:
    python tools/lint-html.py [lessons/specific-file.html]
    python tools/lint-html.py  # checks all lessons/*.html

Exit codes: 0 = pass, 1 = failures found
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = PROJECT_ROOT / "lessons"


def check_contains(html: str, pattern: str, description: str) -> str | None:
    """Return error message if pattern not found in html."""
    if pattern not in html:
        return f"Missing: {description}"
    return None


def check_regex(html: str, pattern: str, description: str) -> str | None:
    """Return error message if regex doesn't match."""
    if not re.search(pattern, html):
        return f"Missing: {description}"
    return None


def lint_lesson(path: Path, html: str) -> list[str]:
    """Lint a lesson page (NNNN-slug.html)."""
    errors = []
    checks = [
        lambda h: check_contains(h, 'href="../assets/style.css"', "style.css link"),
        lambda h: check_contains(h, 'lesson-actions.js"', "lesson-actions.js script"),
        lambda h: check_contains(h, 'theme-toggle.js"', "theme-toggle.js script"),
        lambda h: check_regex(h, r"<h1[^>]*>.+</h1>", "<h1> element"),
        lambda h: check_contains(h, 'id="glossary-data"', "glossary-data JSON block"),
        lambda h: check_contains(h, 'glossary.js"', "glossary.js script"),
    ]
    for check in checks:
        err = check(html)
        if err:
            errors.append(err)
    return errors


def lint_map(path: Path, html: str) -> list[str]:
    """Lint a map page (*-map.html)."""
    errors = []
    checks = [
        lambda h: check_contains(h, 'href="../assets/style.css"', "style.css link"),
        lambda h: check_contains(h, 'theme-toggle.js"', "theme-toggle.js script"),
        lambda h: check_regex(h, r'class="map-graph"', "SVG with class='map-graph'"),
        lambda h: check_contains(h, 'id="gen-modal"', "generation modal"),
        lambda h: check_contains(h, 'id="detail-panel"', "detail panel"),
        lambda h: check_contains(h, '/api/lessons', "/api/lessons detection call"),
    ]
    for check in checks:
        err = check(html)
        if err:
            errors.append(err)
    return errors


def lint_index(path: Path, html: str) -> list[str]:
    """Lint the index page."""
    errors = []
    checks = [
        lambda h: check_contains(h, 'style.css"', "style.css link"),
        lambda h: check_contains(h, 'theme-toggle.js"', "theme-toggle.js script"),
        lambda h: check_regex(h, r"<h1[^>]*>.+</h1>", "<h1> element"),
    ]
    for check in checks:
        err = check(html)
        if err:
            errors.append(err)
    return errors


def classify_and_lint(path: Path) -> list[str]:
    """Classify a file by type and run appropriate linter."""
    name = path.name
    html = path.read_text(encoding="utf-8")

    # Skip spike/test files
    if name.startswith("spike-"):
        return []

    if name == "index.html":
        return lint_index(path, html)
    elif name.endswith("-map.html"):
        return lint_map(path, html)
    elif re.match(r"\d{4}-.+\.html$", name):
        return lint_lesson(path, html)
    else:
        return []  # Unknown type, skip


def main():
    if len(sys.argv) > 1:
        files = [Path(a) for a in sys.argv[1:]]
    else:
        files = sorted(LESSONS_DIR.glob("*.html"))

    total_errors = 0
    checked = 0

    for path in files:
        if not path.exists():
            print(f"  ✗ {path.name}: file not found")
            total_errors += 1
            continue

        errors = classify_and_lint(path)
        if errors:
            total_errors += len(errors)
            for err in errors:
                print(f"  ✗ {path.name}: {err}")
        else:
            if not path.name.startswith("spike-"):
                checked += 1

    print(f"\n{checked} files checked, {total_errors} errors")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
