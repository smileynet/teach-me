#!/usr/bin/env python3
"""verify-links.py — Check that all HTML asset links resolve to existing files.

Finds all <link href> and <script src> with relative paths in HTML files
and verifies the targets exist on disk.

Usage:
  python tools/verify-links.py              # check all HTML files
  python tools/verify-links.py path/to.html  # check one file

Exit codes: 0 = all pass, 1 = broken links found, 2 = error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Patterns to extract relative asset links
LINK_PATTERN = re.compile(r'<link[^>]+href="([^"]+)"', re.IGNORECASE)
SCRIPT_PATTERN = re.compile(r'<script[^>]+src="([^"]+)"', re.IGNORECASE)


def find_html_files(target: str | None = None) -> list[Path]:
    """Find HTML files to check."""
    if target:
        p = Path(target)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return [p] if p.exists() else []

    files = []
    for pattern in ["lessons/**/*.html", "reference/**/*.html", "examples/**/*.html"]:
        files.extend(PROJECT_ROOT.glob(pattern))
    return sorted(files)


def check_file(html_path: Path) -> list[tuple[str, str]]:
    """Check one HTML file. Returns list of (link, reason) for failures."""
    failures = []
    content = html_path.read_text(encoding="utf-8")
    parent = html_path.parent

    for pattern in [LINK_PATTERN, SCRIPT_PATTERN]:
        for match in pattern.finditer(content):
            href = match.group(1)

            # Skip external URLs, data URIs, and anchors
            if href.startswith(("http://", "https://", "data:", "#", "//")):
                continue

            # Resolve relative path
            target = (parent / href).resolve()
            if not target.exists():
                failures.append((href, f"file not found: {target}"))

    return failures


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    files = find_html_files(target)

    if not files:
        print("No HTML files found to check.")
        sys.exit(0)

    total_failures = 0
    checked = 0

    for html_path in files:
        rel_path = html_path.relative_to(PROJECT_ROOT)
        failures = check_file(html_path)
        checked += 1

        if failures:
            for href, reason in failures:
                print(f"  ✗ {rel_path}: {href}")
                print(f"    → {reason}")
            total_failures += len(failures)

    if total_failures == 0:
        print(f"✓ All links verified ({checked} files checked)")
    else:
        print(f"\n✗ {total_failures} broken link(s) in {checked} files")
        sys.exit(1)


if __name__ == "__main__":
    main()
