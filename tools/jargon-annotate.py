#!/usr/bin/env python3
"""Mechanically annotate glossary terms in a lesson HTML file.

Reads the glossary-data JSON block from the file, finds the first occurrence
of each term key in the body text, and wraps it with:
  <span class="term" data-term="KEY">matched text</span>

This is the mechanical part of the jargon skill — it doesn't decide WHICH
terms to define (that's the skill's creative work). It just annotates terms
that already have definitions in the glossary-data block.

Usage:
    python tools/jargon-annotate.py lessons/0001-oidc-auth-flows.html
    python tools/jargon-annotate.py --workspace examples/oidc-rust  # all lessons
    python tools/jargon-annotate.py --dry-run lessons/0001.html     # preview only
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_glossary_data(content: str, filename: str = "") -> dict:
    """Extract the glossary-data JSON from the HTML content."""
    match = re.search(
        r'<script\s+type="application/json"\s+id="glossary-data">\s*(\{.*?\})\s*</script>',
        content, re.DOTALL
    )
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"  ⚠ {filename}: malformed glossary-data JSON: {e}", file=sys.stderr)
        return {}


def find_body_range(content: str) -> tuple[int, int]:
    """Find the range of body content (between <body> and glossary-data script)."""
    body_start = content.find("<body>")
    if body_start == -1:
        body_start = 0
    else:
        body_start += len("<body>")

    # End before the glossary script (don't annotate inside script blocks)
    script_start = content.find('<script type="application/json" id="glossary-data">')
    if script_start == -1:
        script_start = content.find("</body>")
    if script_start == -1:
        script_start = len(content)

    return body_start, script_start


def is_inside_tag(content: str, pos: int) -> bool:
    """Check if position is inside an HTML tag (between < and >)."""
    # Look backwards for < or >
    i = pos - 1
    while i >= 0:
        if content[i] == ">":
            return False
        if content[i] == "<":
            return True
        i -= 1
    return False


def is_inside_svg(content: str, pos: int) -> bool:
    """Check if position is inside an SVG element. Spans are not valid in SVG."""
    before = content[:pos]
    last_svg_open = before.rfind("<svg")
    last_svg_close = before.rfind("</svg>")
    if last_svg_open == -1:
        return False
    return last_svg_open > last_svg_close


def is_already_annotated(content: str, pos: int) -> bool:
    """Check if this position is already inside a <span class="term"> tag."""
    # Look backwards for closing </span> or opening <span class="term"
    before = content[max(0, pos - 200):pos]
    last_span_open = before.rfind('class="term"')
    last_span_close = before.rfind("</span>")
    if last_span_open == -1:
        return False
    return last_span_open > last_span_close


def annotate_term(content: str, key: str, body_start: int, body_end: int) -> str:
    """Find and annotate the first occurrence of a term in the body."""
    # Build search patterns from the key
    # key might be "progressive-overload" → search for "progressive overload", "Progressive Overload", etc.
    search_text = key.replace("-", " ").replace("_", " ")

    # Search in body region only
    body = content[body_start:body_end]

    # Case-insensitive search for the term
    pattern = re.compile(re.escape(search_text), re.IGNORECASE)
    match = pattern.search(body)

    if not match:
        # Try the raw key as well (for acronyms like "doms", "rir", "mrv")
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        match = pattern.search(body)

    if not match:
        return content

    abs_pos = body_start + match.start()

    # Skip if inside a tag or already annotated
    if is_inside_tag(content, abs_pos):
        return content
    if is_inside_svg(content, abs_pos):
        return content
    if is_already_annotated(content, abs_pos):
        return content

    matched_text = match.group(0)
    replacement = f'<span class="term" data-term="{key}">{matched_text}</span>'

    return content[:abs_pos] + replacement + content[abs_pos + len(matched_text):]


def annotate_file(path: Path, dry_run: bool = False) -> dict:
    """Annotate all glossary terms in a file. Returns report."""
    content = path.read_text(encoding="utf-8")
    glossary = extract_glossary_data(content, path.name)

    if not glossary:
        return {"file": str(path), "status": "skip", "reason": "no glossary-data block"}

    # Remove existing term spans first (idempotent — re-annotate from scratch)
    content = re.sub(
        r'<span class="term" data-term="[^"]*">([^<]*)</span>',
        r'\1',
        content
    )

    body_start, body_end = find_body_range(content)
    annotated = []
    skipped = []

    for key in glossary:
        original = content
        content = annotate_term(content, key, body_start, body_end)
        if content != original:
            annotated.append(key)
            # Recalculate body_end since content length changed
            body_end += len(content) - len(original)
        else:
            skipped.append(key)

    if not dry_run and annotated:
        path.write_text(content, encoding="utf-8")

    return {
        "file": str(path.name),
        "status": "annotated" if annotated else "unchanged",
        "annotated": annotated,
        "skipped": skipped,
    }


def main():
    parser = argparse.ArgumentParser(description="Annotate glossary terms in lesson HTML")
    parser.add_argument("files", nargs="*", help="HTML files to annotate")
    parser.add_argument("--workspace", help="Annotate all lessons in a workspace")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    files = []
    if args.workspace:
        ws = Path(args.workspace)
        if not ws.is_absolute():
            ws = Path.cwd() / ws
        files.extend(sorted(ws.glob("lessons/*.html")))
        # Exclude map/index pages
        files = [f for f in files if not f.stem.endswith("-map") and f.stem != "index"]
    if args.files:
        files.extend(Path(f) for f in args.files)

    if not files:
        print("No files to annotate. Provide file paths or --workspace.")
        sys.exit(1)

    total_annotated = 0
    for f in files:
        if not f.exists():
            print(f"  ⚠ {f}: file not found (skipped)", file=sys.stderr)
            continue
        result = annotate_file(f, dry_run=args.dry_run)
        if result["status"] == "annotated":
            total_annotated += len(result["annotated"])
            prefix = "[dry-run] " if args.dry_run else ""
            print(f"  {prefix}{result['file']}: {len(result['annotated'])} terms ({', '.join(result['annotated'])})")
        elif result["status"] == "skip":
            print(f"  {result['file']}: skipped ({result['reason']})")

    if total_annotated > 0:
        action = "would annotate" if args.dry_run else "annotated"
        print(f"\n✓ {action} {total_annotated} terms across {len(files)} files")
    else:
        print(f"\n✓ {len(files)} files checked, no new annotations needed")


if __name__ == "__main__":
    main()
