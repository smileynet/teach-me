#!/usr/bin/env python3
"""verify-links.py — Check that all HTML asset links resolve to existing files.

Also checks source URLs in JSONL question banks (heading anchors verified
via HTTP HEAD, text-fragment and prose links reported as unchecked).

Finds all <link href> and <script src> with relative paths in HTML files
and verifies the targets exist on disk.

Usage:
  python tools/verify-links.py              # check all HTML + JSONL sources
  python tools/verify-links.py path/to.html  # check one file

Exit codes: 0 = all pass, 1 = broken links found, 2 = error
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = PROJECT_ROOT / "learning-records" / "questions"

# Patterns to extract relative asset links
LINK_PATTERN = re.compile(r'<link[^>]+href="([^"]+)"', re.IGNORECASE)
SCRIPT_PATTERN = re.compile(r'<script[^>]+src="([^"]+)"', re.IGNORECASE)


def _resolve_via_assets_mount(href: str) -> Path | None:
    """Map a link that points into an `assets/` segment onto the real mount.

    `examples/*/assets` is a git symlink checked out as a plain TEXT STUB on
    Windows (a small file containing e.g. "../../assets"), so the per-workspace
    path is a file, not a dir, and disk resolution of `../assets/style.css`
    spuriously misses. serve.py mounts /assets from PROJECT_ROOT/assets
    (serve.py:458); resolve against that to match runtime behavior.

    Returns None if the href does not traverse an `assets/` segment.
    """
    parts = href.replace("\\", "/").split("/")
    if "assets" not in parts:
        return None
    tail = parts[parts.index("assets") + 1:]  # path AFTER the assets segment
    return (PROJECT_ROOT / "assets" / Path(*tail)) if tail else (PROJECT_ROOT / "assets")


def find_html_files(target: str | None = None) -> list[Path]:
    """Find HTML files to check."""
    if target:
        p = Path(target)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return [p] if p.exists() else []

    files = []
    for pattern in ["examples/iceberg-workspace/lessons/**/*.html", "examples/iceberg-workspace/reference/**/*.html", "examples/**/*.html"]:
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
                # `examples/*/assets` is a git symlink checked out as a text stub
                # on Windows, so assets links resolve under a non-directory and
                # spuriously miss. serve.py mounts /assets from PROJECT_ROOT; try
                # that mount before reporting a failure.
                asset_target = _resolve_via_assets_mount(href)
                if asset_target is None or not asset_target.exists():
                    failures.append((href, f"file not found: {target}"))

    return failures


# Pattern for navigation links (a[href]) in HTML body
NAV_LINK_PATTERN = re.compile(r'<a[^>]+href="([^"]+)"', re.IGNORECASE)


def check_duplicate_links(html_path: Path) -> list[tuple[str, str]]:
    """Check for multiple navigation elements linking to the same target.
    
    Flags when 3+ distinct <a href> elements point to the same URL
    (suggests a hardcoded link that should vary per item).
    Excludes breadcrumb nav links (those intentionally repeat parent page links).
    """
    failures = []
    content = html_path.read_text(encoding="utf-8")

    # Remove breadcrumb nav before counting (breadcrumbs legitimately link to parent pages)
    content_no_nav = re.sub(r'<nav class="page-nav"[^>]*>.*?</nav>', '', content, flags=re.DOTALL)

    hrefs = [m.group(1) for m in NAV_LINK_PATTERN.finditer(content_no_nav)]
    # Filter to relative links only (skip external, anchors, assets)
    nav_hrefs = [h for h in hrefs if not h.startswith(("http://", "https://", "#", "data:", "//", "javascript:"))
                 and not h.endswith((".css", ".js"))]

    # Count occurrences
    from collections import Counter
    counts = Counter(nav_hrefs)
    for href, count in counts.items():
        if count >= 3:
            failures.append((href, f"appears {count} times — likely a hardcoded link that should vary per item"))

    return failures


def check_source_links() -> tuple[int, int, int]:
    """Check source URLs in JSONL question files.

    Returns (checked, failures, skipped) counts.
    Heading anchors: HTTP HEAD to verify base URL responds.
    Text-fragment/prose: reported as unchecked (fragile by nature).
    """
    if not QUESTIONS_DIR.exists():
        return 0, 0, 0

    checked = 0
    failures = 0
    skipped = 0
    seen_urls: dict[str, bool] = {}  # cache: base_url -> reachable

    for jsonl_path in sorted(QUESTIONS_DIR.glob("*.jsonl")):
        with open(jsonl_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    card = json.loads(line)
                except json.JSONDecodeError:
                    continue

                sources = card.get("sources")
                if not sources:
                    continue

                for src in sources:
                    url = src.get("url", "")
                    anchor_type = src.get("anchor_type", "prose")

                    if anchor_type in ("text-fragment", "prose"):
                        skipped += 1
                        continue

                    # For heading anchors, check base URL is reachable
                    base_url = url.split("#")[0] if "#" in url else url
                    checked += 1

                    if base_url in seen_urls:
                        if not seen_urls[base_url]:
                            failures += 1
                            rel = jsonl_path.relative_to(PROJECT_ROOT)
                            print(f"  ✗ {rel}:{line_num} — {url}")
                            print(f"    → base URL unreachable: {base_url}")
                        continue

                    try:
                        req = urllib.request.Request(base_url, method="HEAD")
                        req.add_header("User-Agent", "teach-me-verify/1.0")
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            seen_urls[base_url] = resp.status < 400
                    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                        seen_urls[base_url] = False

                    if not seen_urls[base_url]:
                        failures += 1
                        rel = jsonl_path.relative_to(PROJECT_ROOT)
                        print(f"  ✗ {rel}:{line_num} — {url}")
                        print(f"    → base URL unreachable: {base_url}")

    return checked, failures, skipped


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

        # Check for duplicate navigation links (hardcoded link bug)
        dup_failures = check_duplicate_links(html_path)
        if dup_failures:
            for href, reason in dup_failures:
                print(f"  ⚠ {rel_path}: {href}")
                print(f"    → {reason}")
            total_failures += len(dup_failures)

    # Check source links in JSONL files (skip if checking a specific file)
    src_checked, src_failures, src_skipped = 0, 0, 0
    if not target:
        src_checked, src_failures, src_skipped = check_source_links()
        total_failures += src_failures

    if total_failures == 0:
        summary = f"✓ All links verified ({checked} files checked"
        if src_checked:
            summary += f", {src_checked} source URLs verified"
        if src_skipped:
            summary += f", {src_skipped} fragile links skipped"
        summary += ")"
        print(summary)
    else:
        print(f"\n✗ {total_failures} broken link(s) in {checked} files")
        sys.exit(1)


if __name__ == "__main__":
    main()
