---
id: "151"
title: "Feature: dependency-reordered MAP.md for reference-style documents"
status: done
blocked_by: ["148", "149"]
tags: [source-ingest]
---

# Feature: dependency-ordered MAP for reference docs

## What to build

When the document type classifier (#148) identifies a reference-style document (API docs, specs, alphabetical reference), generate MAP.md with topic ordering derived from concept dependencies rather than document order.

## Pipeline

```
chunks.json
  + concept graph (from #149 YAKE + regex)
  + document type = "reference" (from #148)
      │
      ▼
  Topological sort on dependency graph
      │
      ▼
  MAP.md with learning-optimal order
```

## Ordering algorithm

1. Build dependency graph: nodes = chunks, edges = prerequisite relationships
2. Topological sort (respects all prerequisites)
3. Break ties with "foundational-ness" score (frequent + early = more foundational)
4. Group related topics (co-occurring concepts cluster together)

## Acceptance criteria

- [x] Produces different order than document for reference-style docs
- [x] Preserves all prerequisite edges (no topic appears before its deps)
- [x] Produces same order as document for tutorial-style docs (no-op) — via caller routing to map_from_chunks.py
- [x] Human-evaluated: generated order is more learnable than alphabetical/original
- [x] Falls back to document order when dependency signal is weak

## Implementation decisions (from spike #156)

- **Cycle-breaking:** MWFAS iterative (preserves strongest pedagogical edges)
- **Scoring:** Blend freq×position (0.6) + in-degree (0.4)
- **SCC size 2:** Soft prereqs (cut weaker edge, annotate for forward-reference callout)
- **SCC size 3+:** Module grouping (mutually-reinforcing topics, any internal order)
- **Density fallback:** < 0.05 → document order with note
