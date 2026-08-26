---
id: "138"
title: "Spike: auto-generating MAP.md from document structure — heading hierarchy + semantic enrichment"
status: done
blocked_by: ["135"]
tags: [source-ingest]
---

# Spike: MAP.md generation from document structure

## Updated framing (complementary, not competing)

Heading-based and semantic approaches are complementary layers, not alternatives:

1. **Heading hierarchy** provides the backbone — document's own structure becomes the initial topic ordering
2. **Semantic enrichment** adds prerequisite edges, identifies concepts that span multiple sections, and detects when document order doesn't match learning order

The spike validates both layers working together.

## Approach

1. Take chunk_pdf.py output (from spike #137) as input
2. Generate MAP.md from headings (chapters → topics, sections → scope)
3. Enrich with semantic analysis: detect prerequisite inversions (section B references concept from section D), identify cross-cutting concepts, flag sections that should be reordered for learning
4. Output: MAP.md with `prereqs:` field populated from both document structure AND semantic analysis

## Heuristics for when to override document order

- Section references a term not yet introduced → add prerequisite edge
- Section is a "background" or "prerequisites" section → move earlier
- Alphabetical ordering detected → treat as reference (reorder by dependency)
- "Advanced" / "Deep dive" sections → place after all basics

## Acceptance criteria

- [x] Generate MAP.md from chunk_pdf.py output (heading → topic mapping)
- [ ] Prerequisite edges from forward references — DEFERRED to #152 (function exists, not wired into output)
- [x] Output respects document order by default (linear prereq chain)
- [x] Working script: tools/map_from_chunks.py
- [x] Tested on 2 books: Five Lines of Code + Software Mistakes and Tradeoffs
