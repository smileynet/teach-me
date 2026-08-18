---
id: "150"
title: "Feature: generate MAP.md from heading hierarchy (tutorial-style documents)"
status: open
blocked_by: []
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

- [ ] Generates valid MAP.md from chunk JSON
- [ ] Topics ordered by document sequence
- [ ] Prereqs default to "previous topic" (linear chain)
- [ ] Skips front matter, TOC, index chunks (noise filtering)
- [ ] Output parseable by existing map_parser.py
- [ ] Tested on 2 books → produces usable topic maps
