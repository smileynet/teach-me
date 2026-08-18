#!/usr/bin/env python3
"""map_from_chunks.py — Generate MAP.md from chunked document output.

Takes chunk_pdf.py JSON output and produces a MAP.md with:
- Topics from chapter/section headings
- Linear prerequisite chain (document order)
- Why text derived from first sentence of each chunk
- Front matter noise filtered out

Usage:
    python tools/map_from_chunks.py chunks.json --domain "my-domain" --title "My Book" --output maps/my-domain.MAP.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass


# Noise patterns — headings that are front/back matter, not teachable content
SKIP_PATTERNS = {
    "brief contents", "contents", "table of contents", "copyright",
    "dedication", "acknowledgments", "acknowledgements", "about the author",
    "about the authors", "about this book", "about the cover",
    "foreword", "preface", "index", "appendix",
}

# Patterns that indicate a ToC entry (mostly dots/numbers, no real content)
TOC_PATTERN = re.compile(r'^[\d\s\.…·]+$|\.{4,}')


@dataclass
class Topic:
    slug: str
    title: str
    why: str
    page: int
    prereqs: list[str]


def slugify(text: str) -> str:
    """Convert heading text to a URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = s.strip('-')[:60]
    return s


def is_noise(heading: str, word_count: int, page: int = 0, total_chunks_on_page: int = 1) -> bool:
    """Determine if a chunk is front/back matter noise."""
    h_lower = heading.lower().strip(". 0123456789")
    if h_lower in SKIP_PATTERNS:
        return True
    if TOC_PATTERN.match(heading):
        return True
    # Pure numbers (page numbers from ToC)
    if heading.strip().isdigit():
        return True
    # Very short content with dots (ToC entries)
    if '...' in heading or '…' in heading:
        return True
    # Tiny chunks that are likely noise
    if word_count < 20:
        return True
    # "About the cover" and similar
    if "cover" in h_lower and ("illustration" in h_lower or "image" in h_lower):
        return True
    return False


def extract_why(content: str, max_length: int = 120) -> str:
    """Extract a concise 'why' statement from chunk content."""
    # Take first non-empty sentence
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and not s.startswith('©') and not s.startswith('Licensed'):
            if len(s) > max_length:
                return s[:max_length].rsplit(' ', 1)[0] + '...'
            return s
    return "Core concepts and techniques"


def detect_forward_references(content: str, all_headings: list[str]) -> list[str]:
    """Find explicit references to other sections in the content."""
    refs = []
    patterns = [
        r'(?:see|refer to)\s+(?:chapter|section|§)\s*(\d+)',
        r'(?:as (?:we\'ll see|described|discussed) in)\s+(?:chapter|section)\s*(\d+)',
        r'(?:requires?|builds? on|depends? on)\s+(?:chapter|section)\s*(\d+)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            refs.append(match.group(1))
    return refs


def generate_map(chunks: list[dict], domain: str, title: str) -> str:
    """Generate MAP.md from chunk list."""
    # Detect ToC pages: pages with many small chunks are likely table of contents
    from collections import Counter
    page_chunk_counts = Counter(c.get("page_start", 0) for c in chunks)
    toc_pages = {p for p, count in page_chunk_counts.items() if count >= 4}

    # Filter noise and ToC
    content_chunks = []
    seen_titles = set()
    for chunk in chunks:
        page = chunk.get("page_start", 0)
        heading = chunk["heading"]

        # Skip ToC pages entirely
        if page in toc_pages:
            continue

        if is_noise(heading, chunk.get("word_count", 0), page):
            continue

        # Only include chapters and substantial sections
        if chunk.get("level", 1) <= 2 and chunk.get("word_count", 0) >= 50:
            # Deduplicate: skip if we've seen a very similar title
            title_key = slugify(heading)
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            content_chunks.append(chunk)

    if not content_chunks:
        print("Warning: no content chunks found after filtering")
        return ""

    # Build topics
    topics: list[Topic] = []
    all_headings = [c["heading"] for c in content_chunks]

    for i, chunk in enumerate(content_chunks):
        slug = slugify(chunk["heading"])
        if not slug:
            continue

        # Deduplicate slugs
        existing_slugs = [t.slug for t in topics]
        if slug in existing_slugs:
            slug = f"{slug}-{chunk.get('page_start', i)}"

        why = extract_why(chunk.get("content", ""))
        prereqs = [topics[-1].slug] if topics else []

        topics.append(Topic(
            slug=slug,
            title=chunk["heading"],
            why=why,
            page=chunk.get("page_start", 0),
            prereqs=prereqs,
        ))

    # TODO(#152): Forward reference detection deferred to ticket 152 (prerequisite edge detection).
    # detect_forward_references() exists but edges are not wired into prereqs yet.

    # Generate MAP.md
    lines = [
        "---",
        f"domain: {domain}",
        f'description: "{title}"',
        "---",
        "",
        f"# {title}",
        "",
        "## Topics",
        "",
    ]

    for topic in topics:
        lines.append(f"### {topic.title}")
        lines.append(f"- **why:** {topic.why}")
        lines.append(f"- **status:** not-started")
        if topic.prereqs:
            lines.append(f"- **prereqs:** {', '.join(topic.prereqs)}")
        lines.append(f"- **source_page:** {topic.page}")
        lines.append("")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/map_from_chunks.py <chunks.json> --domain SLUG --title TITLE [--output path]")
        sys.exit(0)

    chunks_path = Path(args[0])
    if not chunks_path.exists():
        print(f"File not found: {chunks_path}")
        sys.exit(1)

    domain = "untitled"
    title = "Untitled"
    output_path = None

    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--title" in args:
        title = args[args.index("--title") + 1]
    if "--output" in args:
        output_path = Path(args[args.index("--output") + 1])

    chunks = json.loads(chunks_path.read_text())
    map_md = generate_map(chunks, domain, title)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(map_md)
        print(f"✓ Generated {output_path} ({len([l for l in map_md.split(chr(10)) if l.startswith('###')])} topics)")
    else:
        print(map_md)


if __name__ == "__main__":
    main()
