---
id: "312"
title: "Topic: consuming-glTF-engine-import (how a runtime ingests glTF; Godot as one consumer)"
status: in_progress
blocked_by: ["310"]
priority: medium
validation_criteria:
  - "Lesson teaches glTF->engine-node mapping (GLTFDocument->GLTFState->tree in Godot as the worked example), where engines diverge from spec, the don't-hand-edit-imported-data contract; deliberately thin on Godot mechanics (points to godot-asset-pipeline #305)"
  - "Runnable artifact: a stdlib oracle asserting the glTF->node mapping claims; leads_to godot-asset-pipeline"
tags: ["content"]
---

# Topic: consuming-glTF-engine-import (how a runtime ingests glTF; Godot as one consumer)

The other end of the round trip — how an engine turns glTF into a scene. Godot is the worked
example, framed as **"one consumer of many."** Deliberately thin on Godot mechanics — those live
in godot-asset-pipeline (#305).

> **Prereqs:** #310 (anatomy). **`leads_to: godot-asset-pipeline`** (feeds #305 topic 1).

## Source

`.scratch/research/gltf-godot-import.md`; docs.godotengine.org 4.7 (GLTFDocument, Available 3D Formats).

## What to teach

- **The general ingest contract:** a runtime maps glTF concepts → engine scene nodes; the importer
  is a translator, and you **don't hand-edit imported data** (fix upstream).
- **The mapping (Godot as example):** scene→Node3D, node→Node3D, mesh→MeshInstance3D,
  skin→Skeleton3D, light→Light3D (KHR_lights_punctual), camera→Camera3D, material→StandardMaterial3D,
  animation→AnimationPlayer. `GLTFDocument → GLTFState → generate_scene()`.
- **Where engines diverge from spec:** default material remap vs custom-shader passthrough; root
  node modes; extension support varies per engine (a KHR_ the exporter emits may be ignored on import).
- **Editor vs runtime import:** editor adds the ResourceImporterScene layer (name-suffixes, material
  extraction, LOD); runtime `append_from_file → generate_scene` skips it.
- **Explicit handoff:** the Godot *mechanics* (`.import` sidecars, UID, name-suffixes, `.godot`
  cache) are **#305's** job — this topic points there, doesn't re-teach them.

## Runnable artifact (ADR-0010)

A stdlib oracle asserting the glTF→node mapping *claims* (e.g. every glTF `mesh` has a node
referencing it; every `skin` node has a mesh) on a real `.glb` — engine-agnostic, no Godot needed.
Downloadable at `reference/code/gltf-format/consuming-gltf-engine-import/`.

## Acceptance criteria

- [ ] Lesson teaches the general ingest contract + the glTF→engine-node mapping (Godot as "one consumer"), editor-vs-runtime import, and where engines diverge from spec
- [ ] Explicitly defers Godot import mechanics to godot-asset-pipeline (#305) — no duplication
- [ ] Runnable artifact: engine-agnostic oracle asserting the mapping claims; leads_to godot-asset-pipeline recorded
- [ ] Cites GLTFDocument + Available 3D Formats (Godot 4.7)
- [ ] `mise run verify` passes; MAP.md gets lesson_file on completion

## Notes

- The seam to #305: this topic is the spec-side "how import works"; #305 t1 is the Godot-side "which
  format for Godot + verify it imported."
- **Doc-review (2026-09-05, `.scratch/review/godot-docs-verify.md` vs local `.references/godot-docs`):**
  runtime API (`GLTFDocument→GLTFState→generate_scene`, exact signatures) and the full name-suffix
  vocabulary (incl. case-insensitivity + `-`/`$`/`_` separators + the `use_name_suffixes` opt-out) are
  confirmed **[L4:verified]**. TWO corrections to fold in when authoring:
  (1) **Do NOT overstate a "-colonly broken on glTF" caveat** — the official docs do NOT say that; only
  the empty-object→primitive-collision variant is qualified as "with Collada files." Base `-colonly`
  (remove mesh → StaticBody3D) is format-agnostic. (This drops an overstatement from the earlier #305/#311
  research that leaned on GH issue #115869.)
  (2) Downgrade two node-mapping rows to **[L4:inferred]**: `scene→Node3D` (Node3D is the *recommended*
  Root Type, not mandated) and the concrete `Light3D` subclass names (only `GLTFLight` + Blender
  directional/omni/spot are in the reviewed RSTs). Everything else in the mapping stays verified.
