#!/usr/bin/env python3
"""Inject breadcrumb navigation into existing lesson/reference/quiz HTML files.

Does NOT fully re-wrap pages (they already have correct boilerplate from ticket 127).
Just adds the <nav class="page-nav"> breadcrumb that the template now provides.

Usage:
    python tools/migrate-add-breadcrumbs.py --workspace workspace
    python tools/migrate-add-breadcrumbs.py --workspace library/iceberg-workspace
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from lib.page_template import _breadcrumb, _esc


def detect_page_type(path: Path, content: str) -> str | None:
    """Detect page type from path and content."""
    name = path.name
    rel = str(path)
    if "/quiz/" in rel or "-quiz.html" in name:
        return "quiz"
    if "/reference/" in rel:
        return "reference"
    if "-map.html" in name:
        return "map"
    if name == "index.html":
        return "index"
    if "/lessons/" in rel:
        return "lesson"
    return None


def extract_domain_from_map_files(workspace: Path) -> tuple[str, str]:
    """Find domain name and slug from MAP.md files in the workspace."""
    maps_dir = workspace / "maps"
    if maps_dir.exists():
        for f in maps_dir.glob("*.MAP.md"):
            slug = f.stem.replace(".MAP", "")
            content = f.read_text(encoding="utf-8")
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip(), slug
    # Fallback: look for *-map.html in lessons/
    lessons_dir = workspace / "lessons"
    if lessons_dir.exists():
        for f in lessons_dir.glob("*-map.html"):
            slug = f.stem.replace("-map", "")
            # Try to extract title from the HTML
            html = f.read_text(encoding="utf-8")
            title_match = re.search(r'<title>Map:\s*(.+?)</title>', html)
            if title_match:
                return title_match.group(1).strip(), slug
            return slug.replace("-", " ").title(), slug
    return "", ""


def extract_lesson_title(content: str) -> str:
    """Extract title from <h1> tag, stripping any inner HTML markup."""
    match = re.search(r'<h1[^>]*>(.+?)</h1>', content)
    if not match:
        return ""
    # Strip HTML tags (e.g., jargon <span> annotations) to get plain text
    raw = match.group(1).strip()
    return re.sub(r'<[^>]+>', '', raw)


def inject_breadcrumb(path: Path, content: str, domain: str, domain_slug: str) -> str | None:
    """Inject breadcrumb nav into page content. Returns modified content or None if skipped."""
    # Skip if already has breadcrumb
    if 'class="page-nav"' in content:
        return None

    page_type = detect_page_type(path, content)
    if page_type in ("index", None):
        return None  # index has no breadcrumb, unknown pages skip

    title = extract_lesson_title(content)
    if not title:
        return None

    # Build breadcrumb based on page type
    if page_type == "map":
        crumbs = [("All Lessons", "index.html"), (domain or title, None)]
    elif page_type == "lesson":
        map_page = f"{domain_slug}-map.html" if domain_slug else ""
        crumbs = [("All Lessons", "index.html")]
        if domain and map_page:
            crumbs.append((domain, map_page))
        crumbs.append((title, None))
    elif page_type == "reference":
        lesson_id = path.stem
        crumbs = [("All Lessons", f"../lessons/index.html")]
        if domain and domain_slug:
            crumbs.append((domain, f"../lessons/{domain_slug}-map.html"))
        crumbs.append((title, f"../lessons/{lesson_id}.html"))
        crumbs.append(("Reference", None))
    elif page_type == "quiz":
        lesson_id = path.stem.replace("-quiz", "")
        crumbs = []
        if domain and domain_slug:
            crumbs.append(("All Lessons", "../index.html"))
            crumbs.append((domain, f"../{domain_slug}-map.html"))
        crumbs.append((title or lesson_id, f"../{lesson_id}.html"))
        crumbs.append(("Quiz", None))
    else:
        return None

    breadcrumb_html = _breadcrumb(crumbs)

    # Insert after <body>\n\n (the standard opening)
    # Try to find the insertion point: after <body> and any blank line
    match = re.search(r'(<body[^>]*>)\s*\n', content)
    if not match:
        return None

    insert_pos = match.end()
    return content[:insert_pos] + "\n" + breadcrumb_html + content[insert_pos:]


def main():
    args = sys.argv[1:]

    workspace = PROJECT_ROOT / "workspace"
    if "--workspace" in args:
        idx = args.index("--workspace")
        if idx + 1 < len(args):
            workspace = Path(args[idx + 1])
            if not workspace.is_absolute():
                workspace = PROJECT_ROOT / workspace

    dry_run = "--dry-run" in args

    domain, domain_slug = extract_domain_from_map_files(workspace)
    if not domain:
        print(f"⚠ Could not detect domain from {workspace}")

    # Find all HTML files
    updated = 0
    skipped = 0
    html_files = sorted(
        list((workspace / "lessons").rglob("*.html")) +
        list((workspace / "reference").rglob("*.html"))
        if (workspace / "reference").exists() else
        list((workspace / "lessons").rglob("*.html"))
    )

    for f in html_files:
        content = f.read_text(encoding="utf-8")
        result = inject_breadcrumb(f, content, domain, domain_slug)
        if result is None:
            skipped += 1
            continue
        if dry_run:
            print(f"  [dry-run] {f.relative_to(workspace)}")
        else:
            f.write_text(result, encoding="utf-8")
            print(f"  ✓ {f.relative_to(workspace)}")
        updated += 1

    action = "would update" if dry_run else "updated"
    print(f"\n{action} {updated} files, skipped {skipped}")
    if domain:
        print(f"Domain: {domain} ({domain_slug})")


if __name__ == "__main__":
    main()
