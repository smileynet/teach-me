"""chunk_text.py — Chunk Markdown, HTML, and plain text into structured segments.

Produces the same output format as chunk_pdf.py:
  {"heading": str, "level": int, "page_start": int, "content": str,
   "word_count": int, "has_code": bool, "has_table": bool}

Usage:
    from tools.chunk_text import chunk_markdown, chunk_html, chunk_plaintext
"""

from __future__ import annotations

import re
from pathlib import Path


def chunk_markdown(text: str) -> list[dict]:
    """Split markdown on headings (#, ##, ###). Preserves code blocks intact."""
    chunks = []
    current_heading = "Introduction"
    current_level = 1
    current_lines: list[str] = []
    in_code_block = False

    for line in text.split("\n"):
        # Track fenced code blocks (don't split inside them)
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        if in_code_block:
            current_lines.append(line)
            continue

        # Detect heading
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading_match:
            # Flush previous chunk
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append(_make_chunk(current_heading, current_level, content, len(chunks)))
            # Start new chunk
            current_level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Flush final chunk
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append(_make_chunk(current_heading, current_level, content, len(chunks)))

    return chunks


def chunk_html(html: str) -> list[dict]:
    """Split HTML on heading tags (h1-h3). Strips tags from content."""
    # Remove script, style, nav, footer, header
    cleaned = re.sub(
        r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>",
        "", html, flags=re.DOTALL | re.IGNORECASE
    )

    # Extract body/main/article if present
    for tag in ("main", "article", "body"):
        match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", cleaned, re.DOTALL | re.IGNORECASE)
        if match:
            cleaned = match.group(1)
            break

    # Split on h1-h3
    parts = re.split(r"(<h[1-3][^>]*>.*?</h[1-3]>)", cleaned, flags=re.IGNORECASE)

    chunks = []
    current_heading = "Introduction"
    current_level = 1
    current_content = ""

    for part in parts:
        heading_match = re.match(r"<h([1-3])[^>]*>(.*?)</h[1-3]>", part, re.IGNORECASE | re.DOTALL)
        if heading_match:
            # Flush previous
            if current_content.strip():
                text = _strip_html(current_content)
                if text:
                    chunks.append(_make_chunk(current_heading, current_level, text, len(chunks)))
            current_level = int(heading_match.group(1))
            current_heading = _strip_html(heading_match.group(2)).strip()
            current_content = ""
        else:
            current_content += part

    # Flush final
    if current_content.strip():
        text = _strip_html(current_content)
        if text:
            chunks.append(_make_chunk(current_heading, current_level, text, len(chunks)))

    return chunks


def chunk_plaintext(text: str) -> list[dict]:
    """Split plain text on double newlines (paragraphs). First line of each block is heading."""
    blocks = re.split(r"\n{2,}", text.strip())
    chunks = []

    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue
        heading = lines[0].strip()[:80]
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else lines[0]
        if content:
            chunks.append(_make_chunk(heading, 2, content, len(chunks)))

    return chunks


def _make_chunk(heading: str, level: int, content: str, index: int) -> dict:
    """Create a chunk dict matching chunk_pdf.py format."""
    has_code = bool(re.search(r"```|    \w|<code|<pre", content))
    has_table = bool(re.search(r"\|.*\|.*\||<table", content))
    word_count = len(content.split())

    return {
        "heading": heading,
        "level": level,
        "page_start": index + 1,
        "content": content,
        "word_count": word_count,
        "has_code": has_code,
        "has_table": has_table,
    }


def _strip_html(html: str) -> str:
    """Remove HTML tags, collapse whitespace."""
    # Preserve code block content
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&#\d+;", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n ", "\n", text)
    return text.strip()
