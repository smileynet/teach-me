---
id: "266"
title: "Global map Phase 2: concept-based cross-domain edges (author-confirmed suggestions)"
status: open
blocked_by: ["155"]
priority: low
type: feature
tags: ["platform"]
---

# Global map Phase 2: concept-based cross-domain edges

Follow-up to #155 (Phase 1 shipped structural edges: parent/child + `leads_to`). This adds
COMPUTED cross-domain connections from shared concepts / first-mention prereq bridges.

## Key constraint (research, .scratch/research/cross-domain-edges.md)

Similarity asserts *relatedness*, not *dependency*. On a small corpus, semantic-similarity
networks go near-complete and thresholds are unstable → high false-positive risk. Therefore:

- **Computed edges are SUGGESTIONS, never auto-committed edges.** Surface as a distinct
  visual layer ("suggested — unverified"), require author confirmation to promote to a real
  edge. Explicit/structural edges (Phase 1) stay the primary, trusted layer.

## What to build

- Cache per-domain concepts (`.concepts.json`) via existing `extract_concepts.py`.
- `tools/cross_domain_edges.py`: detect shared-concept overlap + first-mention prereq
  bridges across domains; emit candidate edges with evidence + confidence.
- High confidence threshold; sub-threshold links shown as unverified suggestions only.
- Render suggestion edges distinctly in GlobalMapView (dashed/muted, hover-to-explain,
  "confirm" affordance).

## Acceptance criteria

- [ ] Per-domain `.concepts.json` cache generated + reused
- [ ] Shared-concept + prereq-bridge candidate edges detected with evidence + confidence
- [ ] Candidates render as SUGGESTIONS (visually distinct), never auto-promoted to edges
- [ ] Author-confirm promotes a suggestion to a real (structural) edge
- [ ] `mise run verify` EXIT 0
