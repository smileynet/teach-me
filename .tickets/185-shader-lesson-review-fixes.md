---
id: "185"
title: "Fix verified prose errors in shader lessons (review findings)"
status: done
blocked_by: []
priority: high
validation_criteria:
  - "0003 exercise no longer claims ALBEDO defaults to black"
  - "toon-outlines README renderer support matches official docs (Forward+ only)"
  - "band-count wording corrected in 0004"
  - "JFA pass-count example arithmetic corrected in 0007"
  - "detection-pass comment matches code in 0007"
tags: [toon-shaders]
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

## Research findings (2026-08-23)

Subagent research confirmed all claims in the ticket via official docs + prior art:

### F1 — ALBEDO default
**Confirmed white.** Godot 4 spatial shader docs, Fragment built-ins table:
"ALBEDO … Albedo (default white). Base color." Consistent across all 4.x versions.
BaseMaterial3D.albedo_color also defaults to Color(1,1,1,1).

**Exercise implication:** A shader with only `light()` and no `fragment()` renders as
**white toon-banded** (not black). The exercise premise ("mesh renders solid black")
is factually wrong. The fix (add fragment() to sample texture) is still valid, but
the observable symptom changes from "black" to "flat white, no texture visible."

### F4 — Band count math
**Confirmed off-by-one.** `floor(x*N)/N` produces N practical shade levels (the N+1th
at exactly NdotL=1.0 is a degenerate single point). The lesson's `/(N-1)` form
produces N levels spanning full [0,1]. Key: "bands" parameter is best explained as
"number of intervals" — 2 intervals = 2 shade levels (not "2 = classic cel" which
implies a binary light/dark split with step()).

Sources: Offscreen Canvas tutorial, Ronja's Improved Toon Light, CaptainProton42's
FlexibleToonShader (Godot), dev.to empirical tests with 3/4/5/10 levels.

### F8 — JFA pass count
**Confirmed ⌈log₂64⌉ = 6, not 7.** The lesson's claim "both need 7 passes" is wrong.
Original Rong & Tan (2006): passes = ceil(log2(N)). Concrete: 32px=5, 64px=6,
65-128px=7, 256px=8. The fix: use widths in the 65-128 band (e.g., "A 100-pixel
outline costs the same as a 65-pixel one — both need 7 passes").

### F3 — View space Z direction
**Confirmed -Z into scene.** Godot uses right-handed Y-up with -Z forward (OpenGL
convention), maintained even on Vulkan backend. VIEW built-in points from fragment
toward camera (+Z in view space).

## Validation plan (test-scene)

Two claims need visual validation (not just doc-checking):

### F1 validation shader (`test-scene/shaders/validation/test_albedo_default.gdshader`)
Shader with ONLY light(), no fragment(). Apply to TestSphere, render.
- **Expected (if docs right):** White sphere with toon bands visible.
- **If black:** docs are wrong and exercise was correct.

### F9 validation shader (`test-scene/shaders/validation/test_posterize_bands.gdshader`)
Fragment() posterizes albedo to 4 levels, light() applies toon banding.
- **Expected (if analysis right):** Banding still visible (NdotL is geometric, independent of albedo).
- **If flat:** the exercise answer was correct and our analysis is wrong.

### Validation method
1. `godot --headless --editor --import --quit` — confirms compilation
2. GDScript (`validate_claims.gd`) that applies shaders to TestSphere, renders 1 frame,
   saves PNG to `test-scene/.scratch/validation/`
3. If headless can't render: dispatch to godot_editor agent or flag for manual check

## Execution order (revised)

1. Create validation shaders + script, attempt render
2. Mechanical fixes: F3, F5, F6, F7, F8, F10 (no judgment needed)
3. F4 — reword band-count explanation per research
4. F2 — rewrite test-scene section against actual fixtures
5. F1 — rewrite exercise per validation result
6. F9 — rewrite exercise answer per validation result
7. `mise run verify` + grep checks
8. Commit

## Acceptance criteria

- [x] F1: 0003 exercise/hint no longer state ALBEDO defaults to black; new text matches "default white" docs line
- [x] F2: 0003 contains no gdhelper-pipeline/street.tscn/CaliforniaAve references
- [x] F3: 0003 glossary view-space entry says −Z into scene
- [x] F4: 0004 states total shades = bands + 1 and drops "bands = 2 = classic cel"
- [x] F5: toon-outlines README.md and 0006 glossary both say Forward+ only (no Mobile)
- [x] F6: 0006 no longer ties depth_test_disabled to Godot 4.4+
- [x] F7: 0007 detection-pass inline comment describes any-color-difference behavior
- [x] F8: 0007 JFA example uses widths where ⌈log₂⌉ equals stated pass count
- [x] F9: 0008 exercise answer's mechanism matches DIFFUSE_LIGHT math (bands survive albedo posterization)
- [x] F10: toon-banding README accurately scopes max()/+= usage
