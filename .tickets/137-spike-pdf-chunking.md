---
id: "137"
title: "Spike: PDF extraction quality — pymupdf vs pdfplumber vs marker for structured chunking"
status: done
blocked_by: ["135"]
tags: [source-ingest]
---

# Spike: PDF extraction quality

## Question to answer

Which Python PDF library produces the best structured chunks for teaching purposes? Test with 3 representative PDFs (technical spec, textbook, API reference).

## Approach

1. Test pymupdf (fitz), pdfplumber, and marker on the same 3 PDFs
2. Evaluate: heading detection accuracy, table extraction, code block preservation, figure caption extraction, page number mapping
3. Measure: speed, dependency weight, output quality
4. Determine: which handles the widest variety of PDF formats

## Acceptance criteria

- [x] Comparison table: pymupdf vs pdfplumber vs marker (3 libraries tested)
- [x] Recommendation: pymupdf (font-size heading detection, 67x faster than marker, accurate)
- [x] Working POC: tools/chunk_pdf.py (heading hierarchy, page numbers, code/table detection)
- [x] Known limitations: ToC noise, scanned PDFs, multi-column (documented in .scratch/research/137-spike-results.md)
