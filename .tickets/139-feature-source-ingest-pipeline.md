---
id: "139"
title: "Feature: source ingest pipeline — read, chunk, index, and preserve source material"
status: open
blocked_by: ["137", "138"]
---

# Feature: source ingest pipeline

## What to build

`tools/lib/source_reader.py` — reads PDF/MD/HTML/URL sources into structured chunks, preserves raw source, builds a searchable chunk index.

Core capabilities:
- Read: PDF (via spike winner), Markdown, HTML, plain text, URL (fetch + parse)
- Chunk: split on headings, preserve metadata (section title, page number, depth)
- Index: JSON manifest mapping section_id → content + position
- Preserve: raw source saved in workspace/sources/{slug}/ for verification

## Acceptance criteria

- [ ] Supports PDF, Markdown, HTML, plain text, and URL inputs
- [ ] Produces structured chunks with section IDs, page numbers, content
- [ ] Raw source preserved in workspace/sources/ (never modified)
- [ ] Chunk index (JSON) enables lookup by section or keyword
- [ ] Handles documents up to ~100 pages / 50K words
- [ ] Graceful failure on unsupported formats (clear error message)
- [ ] Integration test: ingest a real PDF, verify chunk quality
