---
id: "150"
title: "Feature: generate MAP.md from heading hierarchy (tutorial-style documents)"
status: done
blocked_by: []
tags: [source-ingest]
---

# Feature: heading backbone MAP generation

## What to build

`tools/map_from_chunks.py` — takes chunk_pdf.py JSON output, generates a MAP.md respecting the document's heading structure as the topic ordering.

For tutorial-style documents (detected by #148 or assumed by default), the document author has already solved the sequencing problem. We trust their order and add metadata.

## Pipeline

```
chunks.json → map_from_chunks.py → domain.MAP.md
```

For each H1/H2 chunk:
- `title:` from heading text
- `why:` first sentence of content (or LLM-generated from content summary)
- `status:` not-started
- `prereqs:` previous topic in document order (simple chain)
- `scope:` first 2-3 sentences of content

## Acceptance criteria

- [x] Generates valid MAP.md from chunk JSON
- [x] Topics ordered by document sequence
- [x] Prereqs default to "previous topic" (linear chain)
- [x] Skips front matter, TOC, index chunks (noise filtering)
- [x] Output parseable by existing map_parser.py
- [x] Tested on 2 books → produces usable topic maps (4 fixture files: tutorial, reference, mixed, ambiguous)
