#!/usr/bin/env python3
"""chunk_pdf.py — Extract structured teaching chunks from a PDF.

Uses pymupdf for text/structure extraction. Produces JSON chunks with:
- Section heading, page number, content text, word count
- Hierarchy (chapter vs section vs subsection based on font size tiers)

Usage:
    python tools/chunk_pdf.py path/to/file.pdf [--max-pages 50] [--output chunks.json]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf


@dataclass
class Chunk:
    heading: str
    level: int  # 1=chapter, 2=section, 3=subsection
    page_start: int
    content: str = ""
    word_count: int = 0
    has_code: bool = False
    has_table: bool = False


def detect_font_tiers(doc: pymupdf.Document, max_pages: int = 30) -> dict[str, float]:
    """Analyze font sizes to determine heading thresholds for this specific PDF."""
    sizes: list[float] = []
    bold_sizes: list[float] = []

    for page_num in range(min(len(doc), max_pages)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"]).strip()
                if not text or len(text) > 200:
                    continue
                for span in line["spans"]:
                    sizes.append(span["size"])
                    if "bold" in span.get("font", "").lower():
                        bold_sizes.append(span["size"])

    if not sizes:
        return {"body": 10, "h3": 12, "h2": 14, "h1": 18}

    # Body text is the most common size
    size_counts = Counter(round(s, 1) for s in sizes)
    body_size = size_counts.most_common(1)[0][0]

    # Headings are anything significantly larger than body
    distinct_sizes = sorted(set(round(s, 1) for s in sizes if s > body_size + 1), reverse=True)

    # Assign tiers
    h1_threshold = distinct_sizes[0] if distinct_sizes else body_size + 8
    h2_threshold = distinct_sizes[1] if len(distinct_sizes) > 1 else body_size + 4
    h3_threshold = distinct_sizes[2] if len(distinct_sizes) > 2 else body_size + 2

    return {
        "body": body_size,
        "h3": min(h3_threshold, body_size + 2),
        "h2": min(h2_threshold, body_size + 4),
        "h1": min(h1_threshold, body_size + 8),
    }


def is_code_line(spans: list[dict]) -> bool:
    """Detect if a line is code (monospace font)."""
    return any(
        "mono" in s.get("font", "").lower() or
        "courier" in s.get("font", "").lower() or
        "consol" in s.get("font", "").lower()
        for s in spans
    )


def chunk_pdf(pdf_path: Path, max_pages: int = 100) -> list[Chunk]:
    """Extract structured chunks from a PDF."""
    doc = pymupdf.open(pdf_path)
    pages_to_process = min(len(doc), max_pages)

    # Calibrate font size thresholds for this document
    tiers = detect_font_tiers(doc, min(pages_to_process, 30))

    chunks: list[Chunk] = []
    current_heading = "Introduction"
    current_level = 1
    current_content: list[str] = []
    current_page = 1
    has_code = False
    has_table = False

    # Skip common front matter pages (ToC, copyright)
    skip_patterns = {"contents", "table of contents", "copyright", "dedication", "about the"}

    for page_num in range(pages_to_process):
        page = doc[page_num]

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue

            for line in block.get("lines", []):
                spans = line["spans"]
                text = "".join(s["text"] for s in spans).strip()
                if not text:
                    continue

                # Detect font properties
                max_size = max(s["size"] for s in spans)
                is_bold = any("bold" in s.get("font", "").lower() for s in spans)

                # Determine heading level
                heading_level = 0
                if max_size >= tiers["h1"]:
                    heading_level = 1
                elif max_size >= tiers["h2"] or (max_size >= tiers["h3"] and is_bold):
                    heading_level = 2
                elif is_bold and max_size > tiers["body"] and len(text) < 80:
                    heading_level = 3

                # Skip front matter
                if heading_level > 0 and text.lower().strip(". 0123456789") in skip_patterns:
                    continue

                if heading_level > 0 and len(text) > 2 and len(text) < 150:
                    # Flush previous chunk
                    if current_content:
                        content_text = "\n".join(current_content)
                        word_count = len(content_text.split())
                        if word_count > 10:  # Skip tiny chunks
                            chunks.append(Chunk(
                                heading=current_heading,
                                level=current_level,
                                page_start=current_page,
                                content=content_text,
                                word_count=word_count,
                                has_code=has_code,
                                has_table=has_table,
                            ))

                    current_heading = text.strip(". ")
                    current_level = heading_level
                    current_content = []
                    current_page = page_num + 1
                    has_code = False
                    has_table = False
                else:
                    current_content.append(text)
                    if is_code_line(spans):
                        has_code = True

        # Check for tables AFTER processing all text blocks on this page
        # (ensures table metadata is assigned to the current section, not the previous one)
        tables = page.find_tables()
        if tables and tables.tables:
            has_table = True

    # Flush final chunk
    if current_content:
        content_text = "\n".join(current_content)
        word_count = len(content_text.split())
        if word_count > 10:
            chunks.append(Chunk(
                heading=current_heading,
                level=current_level,
                page_start=current_page,
                content=content_text,
                word_count=word_count,
                has_code=has_code,
                has_table=has_table,
            ))

    doc.close()
    return chunks


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/chunk_pdf.py <file.pdf> [--max-pages N] [--output out.json]")
        sys.exit(0)

    pdf_path = Path(args[0])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    max_pages = 100
    output_path = None
    if "--max-pages" in args:
        idx = args.index("--max-pages")
        max_pages = int(args[idx + 1])
    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])

    chunks = chunk_pdf(pdf_path, max_pages)

    # Print summary
    total_words = sum(c.word_count for c in chunks)
    h1s = [c for c in chunks if c.level == 1]
    h2s = [c for c in chunks if c.level == 2]
    h3s = [c for c in chunks if c.level == 3]

    print(f"PDF: {pdf_path.name} ({max_pages} pages processed)")
    print(f"Chunks: {len(chunks)} ({len(h1s)} chapters, {len(h2s)} sections, {len(h3s)} subsections)")
    print(f"Total words: {total_words:,}")
    print(f"Avg chunk: {total_words // len(chunks) if chunks else 0} words")
    print(f"Code blocks: {sum(1 for c in chunks if c.has_code)}")
    print(f"Tables: {sum(1 for c in chunks if c.has_table)}")
    print()

    # Show structure
    print("Structure:")
    for chunk in chunks[:20]:
        indent = "  " * (chunk.level - 1)
        code = " [code]" if chunk.has_code else ""
        table = " [table]" if chunk.has_table else ""
        print(f"  {indent}p{chunk.page_start:>3} [{chunk.word_count:>4}w] {chunk.heading[:60]}{code}{table}")

    if len(chunks) > 20:
        print(f"  ... ({len(chunks) - 20} more)")

    # Save JSON if requested
    if output_path:
        data = [
            {
                "heading": c.heading,
                "level": c.level,
                "page_start": c.page_start,
                "content": c.content,
                "word_count": c.word_count,
                "has_code": c.has_code,
                "has_table": c.has_table,
            }
            for c in chunks
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
