---
id: "260"
title: "Cross-map prereq references fail single-map validate (dangling toon-banding/configurable-banding)"
status: backlog
priority: medium
blocked_by: []
tags: ["platform"]
---

# Cross-map prereq references fail single-map `validate`

## Discovered
During #257 Subtask B (ULID backfill, 2026-08-29). Confirmed PRE-EXISTING — identical
errors on the pre-migration original (`git show HEAD:...`), so this is a data/validation
model issue, not caused by the id work.

## Symptom
`map_parser.validate` reports undefined prereqs on two maps because the referenced topics
live in a SIBLING map, not the same file:

- `examples/godot-gamedev/maps/blender-texture-prep.MAP.md`:
  - `texture-audit` prereq `toon-banding` — undefined
  - `ramp-band-textures` prereq `toon-banding` — undefined
  - `wiring-the-shader` prereq `configurable-banding` — undefined
- `examples/godot-gamedev/maps/godot-mktoon.MAP.md`:
  - `configurable-banding` prereq `toon-banding` — undefined

`toon-banding` / `configurable-banding` are topics in OTHER godot-gamedev maps
(the toon-shaders / mktoon tracks). `validate` is single-map scoped — it only knows the
topics in the file it was handed — so a legitimate cross-map prerequisite reads as dangling.

## The real question (decide before fixing)
Is a cross-map prereq a VALID authoring construct, or a data error?

- **If valid:** validation must resolve prereqs across the whole domain's map set (or the
  global map forest), not per-file. This overlaps the cross-domain edge / global-graph
  work (ADR-0014 `leads_to` is cross-domain; prereqs may need the same treatment). The
  ULID model helps: once #257 lands and a migration/global index exists, `slug→id`
  resolution can span maps.
- **If a data error:** either the prereq should be removed, or these maps should be merged
  / the prereq retargeted to an in-map topic.

## What to build (pending the decision)
- Option A (cross-map is valid): extend `validate` to accept a known-topic set spanning the
  domain's maps (or the global forest), so cross-map prereqs resolve. Report truly-dangling
  refs only. Likely a `validate_forest(maps)` alongside single-map `validate`.
- Option B (data error): fix the 4 references in the two maps and keep validate single-map.

## Out of scope
- #257 (id/edge schema) — this ticket is about validation SCOPE, not the schema. #257's
  single-map cycle/edge checks are unaffected.

## Acceptance criteria
- [ ] Decision recorded (cross-map prereq valid vs data error), with rationale
- [ ] Either `validate` resolves cross-map prereqs against the correct topic set, OR the 4
      references are corrected — no spurious "undefined prereq" on the 9 committed maps
- [ ] `mise run verify` (or a map-validate step) is clean across all committed maps

## Notes
The 4 dangling refs are currently benign (they don't crash generation — `load_map` just
doesn't synthesize an edge for an unresolved slug, and single-map validate is not a hard
gate in `verify`). Prioritize alongside the cross-domain/global-graph work.
