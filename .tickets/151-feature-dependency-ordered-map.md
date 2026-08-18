---
id: "151"
title: "Feature: dependency-reordered MAP.md for reference-style documents"
status: open
blocked_by: ["148", "149"]
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

- [ ] Produces different order than document for reference-style docs
- [ ] Preserves all prerequisite edges (no topic appears before its deps)
- [ ] Produces same order as document for tutorial-style docs (no-op)
- [ ] Human-evaluated: generated order is more learnable than alphabetical/original
- [ ] Falls back to document order when dependency signal is weak
