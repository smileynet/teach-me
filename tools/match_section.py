#!/usr/bin/env python3
"""match_section.py — Match a user query to source chunks by heading.

Scoring cascade:
1. Number extraction: "chapter 3" → headings containing that number
2. Slug containment: "auth" → slugs containing "auth"
3. Substring: case-insensitive heading containment

Usage:
    python tools/match_section.py source-chunks/domain.json "chapter 3"
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def match_sections(chunks: list[dict], query: str) -> list[dict]:
    """Match a user query to chunks by heading.

    Returns matched chunks sorted by relevance (best first).
    """
    if not chunks or not query.strip():
        return []

    query_lower = query.lower().strip()
    scored: list[tuple[float, int, dict]] = []

    # Extract number from query: "chapter 3", "section 2.1", "ch 5"
    num_match = re.search(r"(\d+(?:\.\d+)*)", query_lower)
    query_number = num_match.group(1) if num_match else None

    # Strip common prefixes for the text portion
    text_query = re.sub(
        r"^(chapter|section|ch|§|part|s)\s*\d*[:\.\s]*",
        "", query_lower, flags=re.IGNORECASE
    ).strip()

    for i, chunk in enumerate(chunks):
        heading = chunk.get("heading", "")
        heading_lower = heading.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", heading_lower).strip("-")
        score = 0.0

        # 1. Number match (highest priority)
        if query_number:
            # Exact chapter/section number in heading
            heading_nums = re.findall(r"(\d+(?:\.\d+)*)", heading)
            if query_number in heading_nums:
                score += 10.0
            elif any(n.startswith(query_number) for n in heading_nums):
                score += 5.0

        # 2. Slug containment
        if text_query and text_query in slug:
            score += 3.0
        elif text_query and any(word in slug for word in text_query.split() if len(word) > 2):
            score += 1.5

        # 3. Substring match on full heading
        if text_query and text_query in heading_lower:
            score += 2.0
        elif query_lower in heading_lower:
            score += 2.0

        if score > 0:
            scored.append((score, i, chunk))

    # Sort by score descending, then by document order
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [chunk for _, _, chunk in scored]


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/match_section.py <chunks.json> \"query\"")
        print("\nMatches a section reference to chunks by heading.")
        print("Examples: 'chapter 3', 'auth', 'the caching section'")
        sys.exit(0)

    chunks_path = Path(args[0])
    if not chunks_path.exists():
        print(f"Error: file not found: {chunks_path}", file=sys.stderr)
        sys.exit(1)

    query = args[1] if len(args) > 1 else ""
    if not query:
        print("Error: provide a search query", file=sys.stderr)
        sys.exit(1)

    chunks = json.loads(chunks_path.read_text())
    matches = match_sections(chunks, query)

    if not matches:
        print(f"No sections matching '{query}'")
        print("\nAvailable sections:")
        for c in chunks:
            print(f"  [{c.get('level', '?')}] {c['heading']}")
        sys.exit(1)

    print(f"Matched {len(matches)} section(s) for '{query}':\n")
    for c in matches:
        wc = c.get("word_count", 0)
        print(f"  [{c.get('level', '?')}] {c['heading']} ({wc} words, p.{c.get('page_start', '?')})")


if __name__ == "__main__":
    main()
