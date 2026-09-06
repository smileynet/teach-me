---
id: "305"
title: "Set up godot-asset-pipeline domain (import/export track: MAP + reference project + validation gate)"
status: open
blocked_by: []
priority: medium
validation_criteria:
  - "godot-asset-pipeline.MAP.md exists with 6 topics + prereq edges (passes check-maps-forest)"
  - "Committed char/asset test-project + opt-in headless import validation identified before any lesson generates (ADR-0010)"
  - "Provenance recorded; standalone depth-0; no duplication with blender-texture-prep"
tags: ["content"]
---

# Set up godot-asset-pipeline domain (import/export track: MAP + reference project + validation gate)

Stand up the standalone **`godot-asset-pipeline`** teaching domain — the character-agnostic
"get 3D assets in and out of Godot" track. One of four focused tracks split from the retired
single `godot-3d-character-pipeline` domain (#293, closed; user direction 2026-09-05). This
ticket creates the scaffold + validation gate; the 6 topic tickets are created after sign-off.

**Setup/scaffold + proposal only — NO lessons generated.** Full scope + sources + per-topic
runnable artifacts + open questions: **`.scratch/tracks/asset-pipeline.md`** (subagent deep-dive).

## Domain shape

```yaml
domain: godot-asset-pipeline
description: "Get 3D assets in and out of Godot — format choice, import mechanics, name-suffix hints, LOD, rigged meshes, and round-trip hygiene"
depth: 0
parent: null
leads_to: [godot-3d-animation]   # imported rigged clips feed the animation track
```

Standalone depth-0. Character-agnostic (neutral props + a generic rigged "arm"/"turret").
References — does NOT duplicate — `blender-texture-prep/bake-and-export` (that covers glTF
*texture/color-space* round-trip; this adds meshes, armatures, LOD, collision, reimport).

## Topics + prereq spine (6, from `.scratch/tracks/asset-pipeline.md`)

| # | slug | why (short) | prereqs |
|---|------|-------------|---------|
| 1 | `format-choice-and-blender-export` | glTF/FBX/blend matrix + Blender export prep (backface culling, origin, normals) | [] |
| 2 | `import-process-and-sidecars` | `.import` (commit) vs `.godot/imported` (don't); UID; auto-reimport; ResourceLoader | [1] |
| 3 | `import-dock-and-name-suffixes` | `-col`/`-colonly`/`-navmesh`/`-occ`/`-noimp`/`-loop`… by asset role | [2] |
| 4 | `lod-and-import-optimization` | auto mesh LOD, HLOD visibility ranges, occlusion, collision perf | [3] |
| 5 | `rigged-meshes-and-skeletons` | rest-pose export, Export-Deform-Bones-Only gotcha, BoneMap retarget | [3] (soft [2]) |
| 6 | `reimport-and-round-trip-hygiene` | iterate loop, reimport-multiple, reverse glTF export, VCS hygiene | [2] (soft [5]) |

Prereq edges: `1→2→3→4`; `3→5`; `2→6` (`5→6` soft). All within-map.

## Runnable-artifact validation gate (ADR-0010)

Committed **test-project** (sibling to `ink-test-project/`, NOT `.references/` — that's
clone-only and can't rehydrate a scaffold). Opt-in `asset:validate-gd` mise task modeled on
`ink:validate-gd` (`godot --headless --editor --import --quit --path .` run twice; import exit
code untrusted; a harness scene asserts node-tree state — StaticBody3D/CollisionShape3D present
for `-col`, `-noimp` node absent, LOD level count > 1, Skeleton3D+AnimationPlayer for rigged).
Guard with `resolve_godot()`→SKIP→return 0. NOT in core `verify`, NOT in CI (no Godot on runner).
`.blend`-sourced lessons SKIP where Blender absent (like the Blender track). Answer BEFORE lessons.

## Acceptance criteria

- [ ] `godot-asset-pipeline.MAP.md` at `library/godot-asset-pipeline/maps/` with all 6 topics + prereq edges; ULIDs via `tools/migrate_map_ids.py --apply`; passes `tools/check-maps-forest.py`
- [ ] Committed asset test-project + opt-in `asset:validate-gd` task identified/recorded (ADR-0010 gate answered)
- [ ] Standalone depth-0 confirmed; differentiated from blender-texture-prep (no duplication)
- [ ] Provenance recorded (test asset sources/licenses; design source `.scratch/tracks/asset-pipeline.md`)
- [ ] The 6 open questions in the scope doc resolved or explicitly deferred (Godot version pin, headless 3D import support, .blend-in-CI, OMI physics, LOD oracle, reverse-export scope)
- [ ] NO lessons generated — 6 topic tickets created after this is signed off

## Update 2026-09-05 — glTF split out to `gltf-format` (#309); this domain SHRINKS

The glTF *standard* content (anatomy, Blender export, skin/morph spec) factored out to the new
standalone engine-agnostic **`gltf-format`** domain (#309, movement-math precedent). This domain
stays Godot-import-**mechanics**-specific and REFERENCES #309. Concretely (per #309 proposal +
`.scratch/research/gltf-domain-boundary.md`):

- **Topic 1** `format-choice-and-blender-export` → **shrinks ~40%**, reframe as
  `format-decision-and-import-verify`: keep the "glTF vs FBX-via-ufbx vs `.blend` vs OBJ/DAE **for
  Godot**" decision + verifying Godot ingested it; the glTF anatomy/exporter walkthrough moves to
  #309. **Gains cross-domain prereq edge from `gltf-format/consuming-glTF-engine-import` (t3).**
- **Topic 5** `rigged-meshes-and-skeletons` → **shrinks to Godot skeleton/BoneMap/retarget
  mechanics only**; the skin/inverse-bind-matrix/rest-pose *why* moves to #309.
  **Gains cross-domain prereq edge from `gltf-format/animation-skins-and-morphs` (t5).**
- **Topic 6** `reimport-and-round-trip-hygiene` → references #309 for round-trip fidelity.
- **Topics 2/3/4** unchanged (pure Godot mechanics). Topic 4's Draco/meshopt mention cites
  #309 t6.

Net: ~4 substantial + 2 lighter topics; description tightens to emphasize *Godot import mechanics*;
ADR-0010 validation gate (test-scene/ reuse) untouched. **Sequence: #309 setup + topic tickets
before this domain's topic tickets 1 & 5.** Reflect the shrunk topic table + the two cross-domain
prereq edges in the MAP when it's placed.

## Notes

- Restructured from #293–#295 (closed superseded). Scope: `.scratch/tracks/asset-pipeline.md`.
- glTF split: `.scratch/proposals/309-gltf-format.md`, `.scratch/research/gltf-domain-boundary.md`.
