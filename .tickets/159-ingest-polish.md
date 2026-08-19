---
id: "159"
title: "Polish: ingest pipeline deferred items (section IDs, keyword index, format rejection, PDF test)"
status: open
blocked_by: []
priority: low
---

# Polish: ingest pipeline deferred items

## Context

Ticket #139 was closed with 4 AC items honestly marked incomplete (per Codex review #158). These are polish items that don't block the core pipeline but improve robustness.

## What to build

1. **Chunk section IDs** — Add a stable `section_id` field to each chunk for cross-reference (slug of heading + index)
2. **Keyword lookup index** — Add a search function over chunks (beyond flat JSON array)
3. **Format rejection** — Unknown file extensions get a clear error instead of silent text fallback
4. **PDF integration test** — End-to-end test: ingest a real PDF, verify chunk quality

## Acceptance criteria

- [ ] Each chunk has a `section_id` field (heading slug + disambiguator)
- [ ] `match_section.py` or a new function supports keyword search in chunk content
- [ ] Unsupported file extensions produce a clear error message listing supported formats
- [ ] At least one test ingests a PDF file end-to-end (can use a small fixture PDF)
