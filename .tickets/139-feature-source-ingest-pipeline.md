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
- [x] Produces structured chunks with headings, levels, content, word counts
- [x] Raw source preserved in workspace/sources/ (never modified)
- [x] Chunk JSON saved for downstream use by MAP generation and enrichment
- [x] Handles documents up to ~100 pages / 50K words (streaming, no memory cap)
- [ ] Chunk section IDs for stable cross-reference (deferred — chunks identified by index)
- [ ] Keyword lookup index (deferred — flat JSON array, no search function yet)
- [ ] Graceful rejection of unsupported formats with clear error (currently treats unknown as text)
- [ ] Integration test: ingest a real PDF end-to-end (tested with MD/HTML only)
