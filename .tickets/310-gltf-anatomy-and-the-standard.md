---
id: "310"
title: "Topic: gltf-anatomy-and-the-standard (the .glb/.gltf object model — the hub)"
status: done
blocked_by: ["309"]
priority: medium
validation_criteria:
  - "Lesson teaches scenes->nodes->meshes->accessors->bufferViews->buffers, .glb vs .gltf+bin, +Y-up/meters convention, as a runnable minimal-complete-file walkthrough (indexed triangle)"
  - "Runnable artifact: a stdlib .py that parses a .glb header + asserts structure (gltf-format-oracle pattern); downloadable + py_compile-checked"
tags: ["content"]
---

# Topic: gltf-anatomy-and-the-standard (the .glb/.gltf object model — the hub)

The **hub** of the gltf-format domain — the object model + container layout every other topic
builds on. Taught as a **runnable minimal-complete file** (a single indexed triangle), walked
field-by-field, NOT an abstract schema tour (Khronos glTF-Tutorials pattern).

> **Prereqs:** #309 domain setup. External: general 3D familiarity (anchor: godot-gamedev 0001).

## Source

`.scratch/research/gltf-standard.md` + `.scratch/research/gltf-glb-stdlib-parse.md`;
Khronos glTF 2.0 spec (registry.khronos.org, ISO/IEC 12113:2022). All L2/L4, fetch-verified.

## What to teach

- **The object graph:** scenes → nodes → meshes → primitives; the **buffer → bufferView →
  accessor** indirection (raw bytes → typed slice → interpreted array). Give buffers/bufferViews/
  accessors **its own weight** — it's the hardest concept (Khronos gives it a dedicated section).
- **Container forms:** `.glb` binary (12-byte header: magic `glTF`/version/length + JSON chunk
  `0x4E4F534A` + BIN chunk `0x004E4942`) vs `.gltf`+`.bin`+textures vs embedded. The
  container version 2 ≠ asset.version "2.0" gotcha.
- **Conventions:** +Y-up, right-handed, meters, radians; nodes/assets face +Z (camera looks −Z);
  TRS = T·R·S; sRGB-vs-linear per texture channel (forward-ref to #313).
- **"The JPEG of 3D":** runtime delivery format, not authoring.

## Pedagogy (from `.scratch/research/gltf-teaching-priorart.md`)

Lead with a ~40-line minimal `.gltf` that parses/renders; walk each field with forward-refs;
close the JSON→structure loop; give the learner a **hex dump of a `.glb` header to self-verify**.

## Runnable artifact (ADR-0010)

A stdlib `.py` (the `tools/gltf-format-oracle.py` pattern — `struct`+`json`, no deps) that parses a
`.glb` header + asserts structure (magic, version==2, chunk layout, accessor→bufferView integrity).
Downloadable at `reference/code/gltf-format/gltf-anatomy-and-the-standard/`; py_compile-checked by
`check-lesson-code.py`. A tiny hand-authored `.gltf` fixture (the indexed triangle) ships alongside.

## Acceptance criteria

- [x] Lesson teaches the object graph (incl. buffer/bufferView/accessor with explicit weight), .glb vs .gltf, and the coordinate/units conventions — as a minimal-complete-file walkthrough
- [x] Includes a hex-dump/self-verify beat for the .glb header (byte layout not prose-only)
- [x] Runnable artifact: stdlib .glb-parse+assert .py + a minimal .gltf fixture; downloadable + py_compile-checked; the domain oracle covers it
- [x] Cites the Khronos glTF 2.0 spec
- [x] `mise run verify` gates pass; MAP.md got lesson_file on completion

## Resolution (2026-09-05)

Authored the hub lesson + its runnable artifacts, all validated:

- **Lesson:** `library/gltf-format/lessons/01-gltf-anatomy-and-the-standard.html` — minimal-file-first arc: key-concept → full `triangle.gltf` walkthrough → buffer→bufferView→accessor **inline SVG** (3-row shared byte-axis, hatched padding, the `12×3=36=byteLength` lock-in) + the "why two objects" misconception `.note` → `.gltf` vs `.glb` `.comparison` + **hex-dump self-verify beat** (decode `47 6C 54 46` / `02 00 00 00` by hand) + the container-vs-asset-version gotcha `.note` → stdlib `read_glb.py` block → conventions → **exercise** (2-`<details>` misconception probe: "the `02` is the container version, not the asset version") → Code Files → What's Next.
- **Artifacts** at `reference/code/gltf-anatomy-and-the-standard/`: `triangle.gltf` (canonical Khronos minimal, base64-verified), `triangle.glb` (700 B, generated — 12-byte header + JSON + BIN chunk), `read_glb.py` (stdlib `struct`+`json` parser+asserts), `README.md`.
- **Validation gates (all pass):** `gltf-format-oracle.py` → exit 0 on 5 assets incl. both triangle fixtures (added to `DEFAULT_ASSETS`); `check-lesson-code.py` → `read_glb.py` block compiles; `check-lesson.py` → **12 pass / 0 fail / 0 warn / 2 skip**; `check-svg-vars.py` → clean; `check-maps-forest.py` → all 6 domains clean. MAP got `lesson_file: 01-gltf-anatomy-and-the-standard.html`; map page + indexes regenerated.

**Verification:** `check-lesson.py --workspace library/gltf-format --lesson lessons/01-gltf-anatomy-and-the-standard.html` → "12 pass, 0 fail, 0 warn, 2 skip"; `gltf-format-oracle.py` → "all glTF-2.0 structural contracts hold" exit 0. Proposal: `.scratch/proposals/310-gltf-anatomy-lesson.md`; research: `.scratch/research/gltf-{standard,glb-stdlib-parse,minimal-triangle,accessor-diagram}.md`.

This unblocks the spoke lessons (#311/#312/#313/#314) — all prereq this hub; #315 caps the track.

## Notes

- The hub — #311/#312/#313/#314 all prereq this; #315 caps the track.
