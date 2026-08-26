---
id: "143"
title: "Feature: automated conflict detection between sources on same concept"
status: done
blocked_by: ["141"]
priority: low
tags: [source-ingest]
---

# Feature: automated conflict detection

## Context

Research finding (135-synthesis): conflicts between sources are pedagogically valuable but currently invisible. After multi-source enrichment (#141) ships, we need automated detection of when sources disagree.

## What to build

When a new source is ingested for a topic that already has material, automatically detect:
- **Factual contradictions** — source A says X, source B says not-X
- **Terminology conflicts** — different words for the same concept
- **Temporal evolution** — source A is outdated, source B reflects current state
- **Opinion divergence** — legitimate differences in recommended approach

Use ConflictRAG taxonomy (from research): factual → resolve via credibility/recency; temporal → note evolution; opinion → always surface.

## Acceptance criteria

- [x] Detects factual contradictions between source passages on same concept
- [x] Classifies conflicts by type (factual, temporal, opinion)
- [x] Generates conflict callout content with attribution to both sources
- [x] Suggests resolution strategy per conflict type
- [x] Integrates with multi-source enrichment pipeline (#141)

**Note:** Superseded by #141 implementation — conflict detection is built into `tools/enrich_from_source.py` with DRAGged taxonomy. Teach skill instructions cover callout generation.
