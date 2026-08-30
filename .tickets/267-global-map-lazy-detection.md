---
id: "267"
title: "Global map Phase 3: lazy/triggered connection detection + auto-regen"
status: open
blocked_by: ["266"]
priority: low
type: feature
tags: ["platform"]
---

# Global map Phase 3: lazy/triggered connection detection + auto-regen

Follow-up to #155/#266. Phase 1 = structural edges; Phase 2 = concept-suggestion edges
(computed on demand). This phase makes detection LAZY/TRIGGERED (not O(n²) on every serve)
and optionally auto-regenerates the global map.

## What to build

- Trigger connection detection only when: (a) a new domain is generated → check overlap
  vs existing; (b) a learner completes a domain → "where does this lead?" search;
  (c) explicit `leads_to` always included (already Phase 1).
- Cache results; recompute only the affected pairs, not all pairs.
- Decide + implement auto-regen policy (on domain completion vs explicit `mise run map:global`).

## Open questions (from #155)

- Confidence threshold for showing weak connections by default (default off).
- Auto-regenerate on domain completion, or only explicit request?

## Acceptance criteria

- [ ] Connection detection is triggered (not computed for all pairs on every serve)
- [ ] Newly generated domain triggers an overlap check against existing domains
- [ ] Cached; only affected pairs recomputed
- [ ] Auto-regen policy decided + documented (ADR if it has tradeoffs)
- [ ] `mise run verify` EXIT 0
