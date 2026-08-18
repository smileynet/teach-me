# Spike 137 Results: PDF Extraction Quality

## Winner: pymupdf

**pymupdf** is the recommended library for teach-me's source ingestion pipeline.

### Comparison

| Metric | pymupdf | pdfplumber |
|--------|---------|-----------|
| Heading detection | ✓ Font-size based (accurate) | ✗ Heuristic (274 false positives vs 60 real) |
| Table extraction | ✓ find_tables() API works | ✓ Slightly better table parsing |
| Code detection | ✓ Monospace font detection | ✗ Indentation heuristic only |
| Speed (20 pages) | 700ms | 480ms |
| Page number mapping | ✓ Native | ✓ Native |
| Dependency weight | 15MB (C library) | 8MB (pure Python + Pillow) |
| Heading hierarchy | ✓ Font size → levels | ✗ No size info without char analysis |

### Key insight: per-document font calibration

PDFs have no standard heading markup. The breakthrough approach: **analyze font sizes across the first 30 pages to calibrate thresholds for each specific document.** The most common font size = body text; anything significantly larger = headings. This adapts automatically to any PDF's typography.

### Proof of concept: `tools/chunk_pdf.py`

Working script that:
1. Auto-calibrates font size thresholds per document
2. Detects heading hierarchy (H1/H2/H3) from size + bold
3. Extracts content between headings as chunks
4. Detects code blocks (monospace fonts) and tables (pymupdf find_tables)
5. Reports page numbers per chunk

Tested on two Manning books — produces ~25 chunks for 50 pages with correct chapter/section structure.

### Known limitations

1. **ToC pages** generate noise (page numbers detected as headings) — needs skip heuristic for pages with >10 "headings"
2. **Scanned PDFs** won't work (no text layer) — document this clearly
3. **Multi-column layouts** may interleave columns — pymupdf's block ordering handles most cases
4. **Figures** are detected as blocks but content not extracted — caption text IS captured
5. **Headers/footers** (running text at top/bottom of each page) may bleed into chunks — needs dedup

### Next steps

1. Add front-matter skip (pages 1-5 typically ToC/copyright)
2. Filter ToC noise (chunks that are mostly "." or numbers)
3. Merge adjacent tiny chunks (<50 words) into their neighbor
4. Add to `mise run setup` dependencies: `pymupdf`
5. Integrate into source_reader.py (#139) as the PDF backend
