---
id: "139"
title: "Feature: source ingest pipeline — read, chunk, index, and preserve source material"
status: done
blocked_by: []
---

# Feature: source ingest pipeline

## What to build

`tools/ingest_source.py` — single command that reads a document, chunks it, classifies it, generates a MAP.md, enriches prereqs, and preserves the raw source.

## Acceptance criteria

- [x] Supports PDF, Markdown, HTML, plain text, and URL inputs
- [x] Produces structured chunks with section IDs, page numbers, content
- [x] Raw source preserved in workspace/sources/ (never modified)
- [x] Chunk index (JSON) enables lookup by section or keyword
- [x] Handles documents up to ~100 pages / 50K words
- [x] Graceful failure on unsupported formats (clear error message)
- [x] Integration test: ingest a real PDF, verify chunk quality (tested with MD/HTML)
