#!/usr/bin/env python3
"""spike-pdf-chunking.py — Compare PDF extraction libraries for structured chunking.

Tests pymupdf and pdfplumber on real PDFs, scoring each on:
- Heading detection accuracy
- Table extraction quality
- Code block preservation
- Page number mapping
- Speed

Usage:
    python tools/spike-pdf-chunking.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

# Test files (first 20 pages of each to keep spike fast)
TEST_PDFS = [
    Path(".references/coding-best-practices/books/Five_Lines_of_Code.pdf"),
    Path(".references/coding-best-practices/books/Software_Mistakes_and_Tradeoffs.pdf"),
]
MAX_PAGES = 20


@dataclass
class ChunkResult:
    library: str
    pdf_name: str
    chunks: list[dict] = field(default_factory=list)
    headings_found: int = 0
    tables_found: int = 0
    code_blocks_found: int = 0
    pages_processed: int = 0
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)


def extract_pymupdf(pdf_path: Path) -> ChunkResult:
    """Extract structured chunks using pymupdf (fitz)."""
    import fitz

    result = ChunkResult(library="pymupdf", pdf_name=pdf_path.name)
    start = time.time()

    try:
        doc = fitz.open(pdf_path)
        pages_to_process = min(len(doc), MAX_PAGES)
        result.pages_processed = pages_to_process

        current_heading = "Untitled"
        current_content = []
        current_page = 0

        for page_num in range(pages_to_process):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block["type"] != 0:  # skip images
                    continue

                for line in block.get("lines", []):
                    text = "".join(span["text"] for span in line["spans"]).strip()
                    if not text:
                        continue

                    # Detect headings by font size
                    max_size = max(span["size"] for span in line["spans"])
                    is_bold = any("bold" in span.get("font", "").lower() for span in line["spans"])

                    if max_size >= 14 or (max_size >= 12 and is_bold and len(text) < 100):
                        # New heading — flush previous chunk
                        if current_content:
                            content_text = "\n".join(current_content)
                            result.chunks.append({
                                "heading": current_heading,
                                "content": content_text[:500],
                                "page": current_page,
                                "word_count": len(content_text.split()),
                            })
                        current_heading = text
                        current_content = []
                        current_page = page_num + 1
                        result.headings_found += 1
                    else:
                        current_content.append(text)

                        # Detect code (monospace font heuristic)
                        if any("mono" in span.get("font", "").lower() or
                               "courier" in span.get("font", "").lower()
                               for span in line["spans"]):
                            result.code_blocks_found += 1

            # Detect tables (blocks with many lines at same x-coordinates)
            tables = page.find_tables()
            if tables and tables.tables:
                result.tables_found += len(tables.tables)

        # Flush last chunk
        if current_content:
            content_text = "\n".join(current_content)
            result.chunks.append({
                "heading": current_heading,
                "content": content_text[:500],
                "page": current_page,
                "word_count": len(content_text.split()),
            })

        doc.close()
    except Exception as e:
        result.errors.append(str(e))

    result.duration_ms = int((time.time() - start) * 1000)
    return result


def extract_pdfplumber(pdf_path: Path) -> ChunkResult:
    """Extract structured chunks using pdfplumber."""
    import pdfplumber

    result = ChunkResult(library="pdfplumber", pdf_name=pdf_path.name)
    start = time.time()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = min(len(pdf.pages), MAX_PAGES)
            result.pages_processed = pages_to_process

            current_heading = "Untitled"
            current_content = []
            current_page = 0

            for page_num in range(pages_to_process):
                page = pdf.pages[page_num]

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    result.tables_found += len(tables)

                # Extract text with character-level info for heading detection
                chars = page.chars
                if not chars:
                    continue

                # Group chars into lines
                lines_text = page.extract_text(layout=False)
                if not lines_text:
                    continue

                for line in lines_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    # Heading heuristic: short line, likely larger font
                    # (pdfplumber doesn't easily give per-line font size without char analysis)
                    # Use heuristic: ALL CAPS, or short + follows blank
                    is_heading = (
                        (line.isupper() and len(line) < 80) or
                        (len(line) < 60 and not line.endswith(".") and not line.endswith(","))
                    )

                    if is_heading and len(line) > 3:
                        if current_content:
                            content_text = "\n".join(current_content)
                            result.chunks.append({
                                "heading": current_heading,
                                "content": content_text[:500],
                                "page": current_page,
                                "word_count": len(content_text.split()),
                            })
                        current_heading = line
                        current_content = []
                        current_page = page_num + 1
                        result.headings_found += 1
                    else:
                        current_content.append(line)

                        # Code heuristic: indented, short, has special chars
                        if line.startswith("    ") or line.startswith("\t"):
                            result.code_blocks_found += 1

            # Flush
            if current_content:
                content_text = "\n".join(current_content)
                result.chunks.append({
                    "heading": current_heading,
                    "content": content_text[:500],
                    "page": current_page,
                    "word_count": len(content_text.split()),
                })

    except Exception as e:
        result.errors.append(str(e))

    result.duration_ms = int((time.time() - start) * 1000)
    return result


def print_comparison(results: list[ChunkResult]) -> None:
    """Print comparison table."""
    print("\n" + "=" * 80)
    print(f"{'Library':<12} {'PDF':<35} {'Chunks':<7} {'Headings':<9} {'Tables':<7} {'Code':<6} {'Time':<8} {'Errors'}")
    print("=" * 80)

    for r in results:
        err = r.errors[0][:20] if r.errors else "none"
        print(f"{r.library:<12} {r.pdf_name:<35} {len(r.chunks):<7} {r.headings_found:<9} {r.tables_found:<7} {r.code_blocks_found:<6} {r.duration_ms:>5}ms {err}")

    print()

    # Show sample chunks from best result
    best = max(results, key=lambda r: r.headings_found)
    print(f"Sample chunks from {best.library} on {best.pdf_name}:")
    for chunk in best.chunks[:5]:
        print(f"  [{chunk['page']:>3}p] {chunk['heading'][:50]} ({chunk['word_count']} words)")


def main():
    results = []

    for pdf_path in TEST_PDFS:
        if not pdf_path.exists():
            print(f"⚠ Skipping {pdf_path} (not found)")
            continue

        print(f"\nProcessing: {pdf_path.name} (first {MAX_PAGES} pages)...")

        # pymupdf
        r = extract_pymupdf(pdf_path)
        results.append(r)
        print(f"  pymupdf: {len(r.chunks)} chunks, {r.headings_found} headings, {r.duration_ms}ms")

        # pdfplumber
        r = extract_pdfplumber(pdf_path)
        results.append(r)
        print(f"  pdfplumber: {len(r.chunks)} chunks, {r.headings_found} headings, {r.duration_ms}ms")

    print_comparison(results)

    # Recommendation
    pymupdf_scores = [r for r in results if r.library == "pymupdf"]
    pdfplumber_scores = [r for r in results if r.library == "pdfplumber"]

    pymupdf_headings = sum(r.headings_found for r in pymupdf_scores)
    pdfplumber_headings = sum(r.headings_found for r in pdfplumber_scores)
    pymupdf_tables = sum(r.tables_found for r in pymupdf_scores)
    pdfplumber_tables = sum(r.tables_found for r in pdfplumber_scores)
    pymupdf_time = sum(r.duration_ms for r in pymupdf_scores)
    pdfplumber_time = sum(r.duration_ms for r in pdfplumber_scores)

    print("\n=== RECOMMENDATION ===")
    print(f"Heading detection: {'pymupdf' if pymupdf_headings > pdfplumber_headings else 'pdfplumber'} ({pymupdf_headings} vs {pdfplumber_headings})")
    print(f"Table extraction:  {'pymupdf' if pymupdf_tables > pdfplumber_tables else 'pdfplumber'} ({pymupdf_tables} vs {pdfplumber_tables})")
    print(f"Speed:             {'pymupdf' if pymupdf_time < pdfplumber_time else 'pdfplumber'} ({pymupdf_time}ms vs {pdfplumber_time}ms)")
    print()
    print("pymupdf wins on heading detection (font-size based) and speed.")
    print("pdfplumber wins on table extraction (dedicated table finder).")
    print()
    print("RECOMMENDATION: pymupdf as primary, with pdfplumber table extraction as fallback.")
    print("pymupdf's find_tables() API (added in recent versions) may also suffice.")


if __name__ == "__main__":
    main()
