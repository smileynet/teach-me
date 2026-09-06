---
id: "309"
title: "Set up gltf-format domain (engine-agnostic glTF 2.0 standard track: MAP + GLB/JSON oracles + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "gltf-format.MAP.md exists with 6 topics + prereq edges (passes check-maps-forest)"
  - "Stdlib GLB/JSON property-oracle artifacts validated by check-lesson-code.py (py_compile) in verify; optional Khronos Validator / gltf-transform cross-check"
  - "Standalone depth-0, engine-agnostic; leads_to godot-asset-pipeline + godot-3d-animation; #305 topics 1/5 gain cross-domain prereq edges"
tags: ["content"]
---

# Set up gltf-format domain (engine-agnostic glTF 2.0 standard track: MAP + GLB/JSON oracles + validation gate)

Stand up the standalone **`gltf-format`** teaching domain — the glTF 2.0 open standard itself:
the JSON/binary anatomy, Blender→glTF export, glTF→engine import, PBR materials, skins &
animation, and the extension/compression ecosystem. **Engine-agnostic** (glTF is Khronos-ratified,
implemented by Godot/Blender/three.js/Babylon/Unity — it outlives any one engine). The FIFTH
focused track (user-requested deep-dive, 2026-09-05), sibling to #305–#308.

**Setup/scaffold + proposal only — NO lessons.** Full scope + sources + the boundary decision:
**`.scratch/research/gltf-domain-boundary.md`** + `.scratch/research/gltf-{standard,blender-export,godot-import}.md`.

## Why standalone (movement-math precedent, NOT blender-texture-prep)

The deciding test: *does the domain teach something that outlives the engine, or serve one
engine's artifact?* glTF is a cross-engine standard → **standalone depth-0, engine-agnostic**
(the movement-math #308 shape: `parent: null`, `leads_to` the engine tracks that apply it,
validated by a *different tier* — stdlib oracles, not the Godot harness). NOT a depth-1 sub-track
(blender-texture-prep shape, which serves one Godot artifact). A parent+subtracks shape was
rejected — it would wrongly re-absorb the Godot import mechanics already solved in #305.

## Domain shape

```yaml
domain: gltf-format
description: "The glTF 2.0 open standard — JSON/binary anatomy, Blender export, engine import, PBR materials, skins & animation, and the extension/compression ecosystem, engine-agnostic"
depth: 0
parent: null
leads_to: [godot-asset-pipeline, godot-3d-animation]
```

## Topics + prereq spine (6, from `.scratch/research/gltf-domain-boundary.md`)

| # | slug | scope (short) | prereqs |
|---|------|---------------|---------|
| 1 | `gltf-anatomy-and-the-standard` | scenes→nodes→meshes→accessors→bufferViews→buffers; `.glb` vs `.gltf`+bin; +Y-up/meters/+Z-forward; read a `.glb` header in stdlib (the HUB topic) | [] |
| 2 | `authoring-and-blender-export` | Blender glTF exporter options; axis/backface/texture-pack; Principled BSDF→glTF PBR (clean vs lossy vs ignored); what the exporter drops | [1] |
| 3 | `consuming-glTF-engine-import` | how a runtime ingests glTF (Godot as "one consumer of many"); glTF→engine-node mapping; where engines diverge. **Thin on Godot — points to #305** | [1] |
| 4 | `materials-and-textures` | PBR metal-rough model; texture slots; sRGB-vs-linear per slot (the #1 silent bug); ORM packing; `KHR_materials_*` | [1] (soft [2]) |
| 5 | `animation-skins-and-morphs` | skins/joints/inverse-bind-matrices (the spec *why* behind rest-pose + Export-Deform-Bones-Only); samplers/channels; interpolation modes; morph targets | [1] (soft [2]) |
| 6 | `extensions-and-optimization` | `KHR_`/`EXT_` mechanism; Draco + meshopt geometry compression; `KHR_texture_basisu` (KTX2); variants; Khronos Validator + `gltf-transform` (capstone) | [1] (soft [4]) |

Prereq graph: `1→{2,3,4,5}`; `4→6`. Topic 1 is the hub; 2/3/4/5 are parallel facets; 6 is the
capstone. All within-map. External prereq only (general 3D/DCC familiarity; anchor:
godot-gamedev `0001-nodes-and-scenes` or a Blender-basics topic) — depth-0 entry point.

## Runnable-artifact validation gate (ADR-0010) — stdlib oracle tier (NOT the Godot harness)

Like movement-math, glTF-standard content validates best with **pure-Python GLB/JSON property
oracles** (stdlib only) — the cleanest tier per code-validation-teaching.md, and it runs in core
`verify` with no Godot/Blender dependency:
- parse a `.glb` header (magic `glTF`, version, chunk layout) and assert structure;
- assert accessor/bufferView counts, componentType/type, alignment;
- assert a skin carries `inverseBindMatrices`; assert morph-target/animation-sampler presence;
- assert `KHR_draco_mesh_compression` / `KHR_texture_basisu` present after a compression step;
- assert the +Y-up / +Z-forward convention on an exported asset.

Each artifact = a `.py` at `reference/code/gltf-format/{slug}/` printing structured JSON
(`{"status":"pass|fail","metrics":{…}}`, exit 0/1), compile-checked by `tools/check-lesson-code.py`.
**Optional cross-viewer confirmation** (Khronos glTF Validator, `gltf-transform` CLI, model-viewer)
as a Tier-2 opt-in where a real conformance check adds signal. Godot import is then just ONE
downstream consumer, proven by #305's existing harness — complementary tiers.

## Cross-domain wiring

- `leads_to: [godot-asset-pipeline, godot-3d-animation]` — engine tracks CONSUME the standard.
  Topic 3 (`consuming-glTF-engine-import`) feeds #305 topic 1; topic 5 (`animation-skins-and-morphs`)
  feeds #305 topic 5 (rigged meshes) + #306 (AnimationPlayer/library work).
- **#305 shrinks in response** (already noted in its proposal Addendum 2): topic 1 → ~40% lighter
  (`format-decision-and-import-verify`), topic 5 → Godot skeleton/retarget mechanics only, topic 6
  references glTF for round-trip fidelity. #305 gains two cross-domain prereq edges FROM this domain.
- **Sequencing:** create/scaffold this domain BEFORE #305's topic tickets, since #305 t1/t5 prereq it.

## Acceptance criteria

- [ ] `gltf-format.MAP.md` at `library/gltf-format/maps/` with all 6 topics + prereq edges; ULIDs via `tools/migrate_map_ids.py --apply`; passes `tools/check-maps-forest.py`
- [ ] Stdlib GLB/JSON oracle artifact convention confirmed (structured JSON + exit code, `check-lesson-code.py` py_compile in verify); optional Khronos Validator/gltf-transform cross-check tier noted
- [ ] Standalone depth-0, engine-agnostic; `leads_to [godot-asset-pipeline, godot-3d-animation]` set
- [ ] #305 cross-domain prereq edges recorded (t3→#305-t1, t5→#305-t5); #305 shrink coordinated (its Addendum 2)
- [ ] Provenance recorded (registry.khronos.org / KhronosGroup glTF; design sources `.scratch/research/gltf-*.md`)
- [ ] The open questions in the scope docs resolved or deferred (+Z/−Z convention folklore, per-extension ratification status, Draco-vs-meshopt guidance, spec minor-version drift, BRDF-math scope)
- [ ] NO lessons generated — 6 topic tickets created after sign-off

## Notes

- Fifth track from the character-pipeline restructure (#293 closed). Scope:
  `.scratch/research/gltf-domain-boundary.md` (decision) + `gltf-standard.md` / `gltf-blender-export.md` / `gltf-godot-import.md` (content).
