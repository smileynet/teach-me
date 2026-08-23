---
id: "185"
title: "Fix verified prose errors in shader lessons (review findings)"
status: open
blocked_by: []
priority: high
validation_criteria:
  - "0003 exercise no longer claims ALBEDO defaults to black"
  - "toon-outlines README renderer support matches official docs (Forward+ only)"
  - "band-count wording corrected in 0004"
  - "JFA pass-count example arithmetic corrected in 0007"
  - "detection-pass comment matches code in 0007"
---

# Fix verified prose errors in shader lessons (review findings)

## Problem

Full review of all six shader lessons (0003–0008) against their sources
(`examples/godot-gamedev/reference/code/`) and the demo project (`test-scene/`)
found **zero code defects** — every embedded shader matches its source file
semantically or byte-for-byte, and all 15 shaders parse clean under Godot 4.7.1
headless. The defects are all in **prose**: factually wrong claims that a learner
would absorb as truth.

**Intent source:** Discovery — user-requested review session (2026-08-23),
"review all lessons for shaders against their sources, and the example godot
project that demonstrates them".

## Context for a fresh agent

Read first:

1. `examples/godot-gamedev/lessons/0003-spatial-shader-anatomy.html` through `0008-color-simplification.html`
2. `examples/godot-gamedev/reference/code/toon-outlines/README.md`
3. `test-scene/shaders/*.gdshader` (canonical; byte-identical copies live under `reference/code/*/`)

Decision already made: lesson **code stays untouched** — only prose, comments,
READMEs, and glossary entries change unless a criterion says otherwise.

### CRITICAL correction to an earlier sub-agent finding

A review pass initially flagged lesson 0006's "Forward+ only" claim as wrong,
citing the repo's own README ("Forward+ or Mobile"). **Official docs prove the
lesson prose right and the README/glossary wrong.** Do not "fix" 0006's prose to
say Mobile is supported:

- Godot shading-language docs (4.3, 4.4, 4.5, current stable all identical):
  `hint_normal_roughness_texture` — "Texture is the normal roughness texture
  (**only supported in Forward+**)".
- Screen-reading shaders tutorial: "**Normal-roughness texture is only supported
  in the Forward+ rendering method, not Mobile or Compatibility.**"
- godotengine/godot#78411 (+PR #78839): Mobile renderer errors on this hint;
  maintainer: normal-roughness buffer "not supported in the Mobile renderer, and
  we don't expect it to be implemented". Feature request still open:
  godotengine/godot-proposals#11992.

## What to build

Learners reading lessons 0003–0008 are no longer told anything contradicted by
official Godot/GLSL documentation or by the shader code sitting next to the text.
Given any lesson page, When cross-checked against the cited official doc lines,
Then no statement fails the check.

## Findings to fix (each maps to an acceptance criterion)

### F1 · 0003 — ALBEDO default is white, not black (wrong fact)
Lesson line ~185/189 claims unset `ALBEDO` "defaults to `vec3(0,0,0)` (black)"
and builds the exercise answer around it. Official docs, Fragment built-ins
table: "**ALBEDO** … Albedo (**default white**). Base color."
https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/spatial_shader.html
Rewrite symptom ("white where lit, black in shadow, untextured") and answer.

### F2 · 0003 — stale project references
Lines ~204–211 reference a nonexistent *gdhelper-pipeline* project
(`scenes/street.tscn`, `CaliforniaAve`, `Building Front`). Rewrite steps against
`test-scene/scenes/shader_test.tscn` (TestBox/TestSphere, ShaderMaterial +
Shader Parameters workflow) or cut the section.

### F3 · 0003 glossary — view-space Z direction
Glossary defines view space "Z pointing toward the scene". Godot convention is
−Z forward: Node3D.look_at API docs — "local forward axis (**-Z**, Vector3.FORWARD)".
Change to "−Z pointing into the scene."

### F4 · 0004 — band count off-by-one
"`bands` = number of brightness levels… `bands = 2` classic cel" is wrong:
`mod()` snapping yields N lit levels plus the zero/shadow floor = N+1 shades;
`bands=1` reproduces the step() cut, not flat. GLSL spec: mod(x,y) = x − y·floor(x/y)
(https://docs.gl/sl4/mod). Reword bullet + answer; note lesson's own SVG shows 4 bands = bands 3.

### F5 · 0006 README + 0006 glossary — renderer support (see correction above)
- `reference/code/toon-outlines/README.md`: change "Forward+ **or Mobile**" → "Forward+ only".
- 0006 glossary entry: drop "and Mobile"; align with lesson prose (which is correct).

### F6 · 0006 — unverifiable version claim
"In Godot 4.4+, `depth_test_disabled` is required…" has no doc basis; render-modes
table just says "Disable depth testing."
(spatial_shader.html). Drop version framing; keep functional rationale.

### F7 · 0007 — detection-pass comment contradicts its own code
Lesson inline comment says outline only when neighbor is "behind (lower alpha /
black background)"; code (`toon_outline_colorid_detect.gdshader`) outlines on
**any color difference** — and the lesson's own prose two paragraphs later agrees
with the code. Replace comment wording with the source's ("Any color difference means boundary").

### F8 · 0007 — JFA pass-count arithmetic error
"A 100-pixel outline costs the same as a 64-pixel one — both need 7 passes":
⌈log₂64⌉ = 6, contradicting the lesson's own N = ⌈log₂(width)⌉ formula. Use a width
from the 65–128 band (e.g. 65).

### F9 · 0008 — exercise answer describes impossible failure mode
Claimed albedo posterization makes shadow-to-lit bands disappear; but
`DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * bands` keeps spatial
luminance steps regardless of albedo quantization. Real symptom: hue/detail
regions collapse to same value → flat/muddy patches. Reword per actual math.

### F10 · toon-banding README overclaim
"All files use `max()` instead of `+=`" — `toon_test.gdshader:12` uses `+=`
(intentional lesson-3 baseline). Reword: three of four use max().

## Cosmetic backlog (optional, batch at reviewer's discretion)

- 0004: "degrees" → NdotL-space wording for softness; note smoothstep(e,e,x)
  degenerate (GLSL spec: "Results are undefined if edge0 ≥ edge1", docs.gl/sl4/smoothstep).
- 0004 diff block: mark the `+=` → `max(DIFFUSE_LIGHT,…)` change instead of showing as context.
- 0005: naive-projection block tagged `data-file="triplanar_toon.gdshader"` though
  that code isn't in the file; unused NODE_POSITION_WORLD glossary entry;
  "45-degree slope" sharpness framing.
- 0006: "(Sobel)" column mislabel (implementation is opposing-neighbor differencing);
  "same draw call batch" → "second draw of same mesh"; diff block adds comment absent from canonical file.
- 0008: sample-count table cell → `(kernel_size+1)² × 4`.
- palette_snap footnote (lesson AND source): Oklab transform expects linear light
  (Bottosson, https://bottosson.github.io/posts/oklab/) while screen backbuffer is
  sRGB-encoded unless HDR 2D — optional pow(2.2) pre-transform in both copies.

## Fixture gap (out of scope here, noted for planning)

test-scene wires up `toon_bands`, `toon_outline*`, `kuwahara_basic` — but
`toon_test`, `triplanar_toon`, `posterize_*`, `palette_snap`, and the entire
advanced-outline set (colorid/colorid_detect/jfa_pass) are referenced by no scene
or material. Lesson 0007 has no runnable fixture. Separate ticket if wanted.

## Acceptance criteria

- [ ] F1: 0003 exercise/hint no longer state ALBEDO defaults to black; new text matches "default white" docs line
- [ ] F2: 0003 contains no gdhelper-pipeline/street.tscn/CaliforniaAve references
- [ ] F3: 0003 glossary view-space entry says −Z into scene
- [ ] F4: 0004 states total shades = bands + 1 and drops "bands = 2 = classic cel"
- [ ] F5: toon-outlines README.md and 0006 glossary both say Forward+ only (no Mobile)
- [ ] F6: 0006 no longer ties depth_test_disabled to Godot 4.4+
- [ ] F7: 0007 detection-pass inline comment describes any-color-difference behavior
- [ ] F8: 0007 JFA example uses widths where ⌈log₂⌉ equals stated pass count
- [ ] F9: 0008 exercise answer's mechanism matches DIFFUSE_LIGHT math (bands survive albedo posterization)
- [ ] F10: toon-banding README accurately scopes max()/+= usage
