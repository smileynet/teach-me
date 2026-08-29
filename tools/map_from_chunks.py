#!/usr/bin/env python3
"""map_from_chunks.py — Generate MAP.md from chunked document output.

Takes chunk_pdf.py JSON output and produces a MAP.md compatible with
map_parser.py. For tutorial-style documents, trusts the document's
heading structure as the topic ordering.

Usage:
    python tools/map_from_chunks.py chunks.json --domain "my-domain" --title "My Book" [--output path] [--classify]
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from tools.lib import ulid
except ModuleNotFoundError:  # when tools/ is on sys.path directly
    from lib import ulid  # type: ignore[no-redef]


# Noise patterns — headings that are front/back matter, not teachable content
SKIP_PATTERNS = {
    "brief contents", "contents", "table of contents", "copyright",
    "dedication", "acknowledgments", "acknowledgements", "about the author",
    "about the authors", "about this book", "about the cover",
    "foreword", "preface", "index", "appendix", "bibliography",
    "references", "glossary", "summary", "colophon",
}

# Patterns that indicate a ToC entry (mostly dots/numbers, no real content)
TOC_PATTERN = re.compile(r'^[\d\s\.…·]+$|\.{4,}')


@dataclass
class Topic:
    slug: str
    title: str
    why: str
    scope: str
    page: int
    prereqs: list[str]


def slugify(text: str) -> str:
    """Convert heading text to a URL-safe slug."""
    # Strip leading chapter/part numbering
    s = re.sub(r'^(chapter|part)\s+\d+[:\.\s]*', '', text, flags=re.IGNORECASE)
    # Strip section numbering like "1.1", "2.2.1", "3)"
    s = re.sub(r'^[\d]+(?:\.[\d]+)*[:\.\)\s]+', '', s)
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = s.strip('-')[:60]
    return s


def is_noise(heading: str, word_count: int) -> bool:
    """Determine if a chunk is front/back matter noise."""
    h_lower = heading.lower().strip(". 0123456789")
    if h_lower in SKIP_PATTERNS:
        return True
    if TOC_PATTERN.match(heading):
        return True
    if heading.strip().isdigit():
        return True
    if '...' in heading or '…' in heading:
        return True
    if word_count < 20:
        return True
    return False


def derive_scope(word_count: int) -> str:
    """Derive scope from chunk word count."""
    if word_count < 500:
        return "lightweight"
    if word_count > 1500:
        return "deep"
    return "substantial"


def extract_why(content: str, max_length: int = 150) -> str:
    """Extract a concise 'why' statement from chunk content."""
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and not s.startswith('©') and not s.startswith('Licensed'):
            if len(s) > max_length:
                return s[:max_length].rsplit(' ', 1)[0] + '...'
            return s
    return "Core concepts and techniques"


def generate_map(chunks: list[dict], domain: str, title: str) -> str:
    """Generate MAP.md from chunk list.

    Output format matches map_parser.py expectations:
    - YAML frontmatter with domain, description, depth, parent, leads_to, generated
    - ## Orientation section
    - ## Topics with ### slug headings and field lines
    """
    # Detect ToC pages: pages with many small chunks are likely table of contents
    page_chunk_counts = Counter(c.get("page_start", 0) for c in chunks)
    toc_pages = {p for p, count in page_chunk_counts.items() if count >= 5}

    # Filter noise and ToC
    content_chunks = []
    seen_slugs: set[str] = set()
    for chunk in chunks:
        page = chunk.get("page_start", 0)
        heading = chunk["heading"]
        word_count = chunk.get("word_count", 0)

        if page in toc_pages:
            continue
        if is_noise(heading, word_count):
            continue
        # Only include chapters (level 1) and substantial sections (level 2)
        if chunk.get("level", 1) > 2:
            continue
        if word_count < 50:
            continue

        slug = slugify(heading)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        content_chunks.append(chunk)

    if not content_chunks:
        return ""

    # Build topics with linear prerequisite chain
    topics: list[Topic] = []
    for chunk in content_chunks:
        slug = slugify(chunk["heading"])
        why = extract_why(chunk.get("content", ""))
        scope = derive_scope(chunk.get("word_count", 0))
        prereqs = [topics[-1].slug] if topics else []

        topics.append(Topic(
            slug=slug,
            title=chunk["heading"],
            why=why,
            scope=scope,
            page=chunk.get("page_start", 0),
            prereqs=prereqs,
        ))

    # Generate MAP.md
    lines = [
        "---",
        f"domain: {domain}",
        f'description: "{title}"',
        f"generated: {date.today().isoformat()}",
        "depth: 0",
        "parent: null",
        "leads_to: []",
        "---",
        "",
        f"# {title}",
        "",
        "## Orientation",
        "",
        f"Topics derived from document headings in reading order. "
        f"{len(topics)} topics covering {sum(c.get('word_count', 0) for c in content_chunks):,} words.",
        "",
        "## Topics",
        "",
    ]

    for topic in topics:
        prereqs_str = f"[{', '.join(topic.prereqs)}]" if topic.prereqs else "[]"
        lines.append(f"### {topic.slug}")
        lines.append(f"- **id:** {ulid.new()}")
        lines.append(f"- **title:** {topic.title}")
        lines.append(f"- **why:** {topic.why}")
        lines.append(f"- **scope:** {topic.scope}")
        lines.append(f"- **prereqs:** {prereqs_str}")
        lines.append("")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/map_from_chunks.py <chunks.json> --domain SLUG --title TITLE [--output path] [--classify]")
        print("\nOptions:")
        print("  --domain    Domain slug (used in filename and frontmatter)")
        print("  --title     Human-readable title for the map")
        print("  --output    Output path (default: stdout)")
        print("  --classify  Run classify_document.py first; warn if document is reference-style")
        sys.exit(0)

    chunks_path = Path(args[0])
    if not chunks_path.exists():
        print(f"Error: file not found: {chunks_path}", file=sys.stderr)
        sys.exit(1)

    domain = "untitled"
    title = "Untitled"
    output_path = None
    classify = "--classify" in args

    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--title" in args:
        title = args[args.index("--title") + 1]
    if "--output" in args:
        output_path = Path(args[args.index("--output") + 1])

    chunks = json.loads(chunks_path.read_text())

    # Optional classification check
    if classify:
        from classify_document import classify_document
        result = classify_document(chunks)
        if result["type"] == "reference":
            print(f"⚠ Document classified as reference-style (score={result['score']:.2f}, "
                  f"confidence={result['confidence']:.0%})", file=sys.stderr)
            print("  Consider using dependency-reordered MAP generation (#151) instead.",
                  file=sys.stderr)
            print("  Proceeding with heading-backbone order anyway...", file=sys.stderr)
            print(file=sys.stderr)
        elif result["type"] == "mixed" and result.get("split_point") is not None:
            split = result["split_point"]
            print(f"⚠ Mixed document detected (split at chunk {split}: "
                  f'"{chunks[split]["heading"]}")', file=sys.stderr)
            print("  Tutorial section will be used; reference section skipped.",
                  file=sys.stderr)
            print(file=sys.stderr)
            # Trim to tutorial portion
            chunks = chunks[:split]

    map_md = generate_map(chunks, domain, title)

    if not map_md:
        print("Error: no content chunks found after filtering", file=sys.stderr)
        sys.exit(1)

    # Validate output is parseable
    _validate_output(map_md, output_path)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(map_md)
        topic_count = map_md.count("\n### ")
        print(f"✓ Generated {output_path} ({topic_count} topics)")
    else:
        print(map_md)


def _validate_output(map_md: str, output_path: Path | None = None):
    """Verify the generated MAP.md is parseable by map_parser."""
    import tempfile
    tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
    try:
        tmp.write_text(map_md)
        # Import map_parser from tools/
        sys.path.insert(0, str(Path(__file__).parent))
        from map_parser import load_map, validate
        domain_map = load_map(tmp)
        errors = validate(domain_map)
        if errors:
            print(f"⚠ Validation warnings:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Output validation failed: {e}", file=sys.stderr)
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
