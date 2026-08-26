---
id: "152"
title: "Feature: prerequisite edge detection via forward references and first-mention analysis"
status: done
blocked_by: ["149"]
tags: [source-ingest]
---

# Feature: prerequisite edge detection

## What to build

Enrich MAP.md `prereqs:` fields with evidence-based edges detected from document content — beyond the simple "previous topic" default.

Three detection mechanisms:

### 1. Explicit forward references (high confidence)
Regex patterns that catch direct cross-references:
- "see chapter/section N", "as described in §X"
- "requires understanding of X", "builds on X"
- "prerequisite: X", "assumes knowledge of X"

### 2. First-mention analysis (medium confidence)
- Track where each key term is first defined (definition = first use with explanation)
- If chunk B uses term T without definition, and chunk A defines T → B prereqs A
- Uses YAKE concepts as the term set to track

### 3. Foundational-ness scoring (ordering signal)
- Concepts used across many chunks = foundational → appear early
- Concepts used in only 1-2 chunks = specialized → appear after their foundations
- Score: `frequency × (1 / first_appearance_position)`

## Acceptance criteria

- [x] Detects explicit cross-references between sections
- [x] First-mention tracking identifies implicit dependencies
- [x] Foundational-ness score computed per concept
- [x] Outputs prerequisite edges compatible with MAP.md `prereqs:` field
- [x] Validated: edges are plausible (manual review of 10+ detected edges)
- [x] Integrates into map_from_chunks.py as an enrichment step

## Implementation notes

- **Thresholds** (research-backed, Sato et al. 2017): ≥0.7 hard, 0.4-0.7 soft, <0.4 drop
- **Orphans** become entry points (empty prereqs) — research shows >50% of real curriculum nodes are isolated, this is normal
- **Provenance**: auto-generated prereqs tagged with `<!-- auto: enrich_prereqs -->`, manual edits never overwritten
- **Idempotent**: safe to re-run; overwrites only auto-tagged or empty prereqs
- 12 pytest tests pass
