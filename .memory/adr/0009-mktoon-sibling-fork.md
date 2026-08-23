# ADR 0009: MKToon as Sibling Map (Fork from toon-banding)

**Status:** Accepted  
**Date:** 2026-08-23  
**Context:** Ticket #186

## Decision

The MKToon lesson track is a **sibling MAP** to `godot-toon-shaders`, not a continuation of it. Both branch from the `toon-banding` topic (lesson 0004). The learner sees an explicit fork after mastering floor-based quantization: post-process path vs per-material path.

## Context

After completing lessons 0003–0008 (toon shading via filtering), we needed to teach an alternative approach — per-material authored NPR — using a real shipped game's shader (Esoteric Ebb's MK.Toon, reverse-engineered from 838 Unity materials and ported to Godot).

The question: should this be lessons 0009+ in the existing `godot-toon-shaders` track, or a new map?

## Options Considered

### A. Continue existing track (0009+)

- **Pro:** Simple numbering, one MAP file
- **Con:** The existing track has a clear endpoint (color simplification = "complete the flat-color cel look"). Appending a fundamentally different philosophy breaks the narrative arc. Also forces learners through outlines/JFA/Kuwahara before starting the per-material approach — those aren't prerequisites.

### B. New sibling MAP (chosen)

- **Pro:** Each track has a coherent narrative arc. Learner can pick either path after toon-banding without wading through unrelated prerequisites. Fork is explicitly visible on the map.
- **Con:** Two MAPs to maintain. Cross-references needed for shared concepts (inverted hull appears in both).

### C. Child MAP under toon-shaders

- **Pro:** Clear hierarchy
- **Con:** Implies toon-shaders is a prerequisite, which it isn't (only `toon-banding` is needed)

## Consequences

1. `godot-mktoon.MAP.md` is a depth-1 child of `godot-gamedev`, sibling to `godot-toon-shaders`
2. First topic (`configurable-banding`) prereqs `toon-banding` from the sibling map — this is a cross-map prereq reference
3. `godot-toon-shaders` adds `leads_to: [godot-mktoon]` to surface the fork
4. The parent map page (when #155 is implemented) will render this as a visible fork from `toon-banding`
5. Lesson numbering continues at 0009 within the `godot-gamedev` domain folder (filesystem simplicity)
6. Shared techniques (inverted hull) are re-taught in the MKToon context, not cross-referenced to lesson 0006 — each track should be self-contained enough to follow independently

## Related

- #155 (global map) — concrete use case for sibling-fork rendering
- #055 (cross-domain links) — mechanism #4 for detecting cross-map prereq references
