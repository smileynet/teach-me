---
id: "220"
title: "Lesson: Authoring Toon Control Maps — Ramp, Noise, Threshold (0018)"
type: feature
status: in_progress
priority: high
blocked_by: ["217"]
parent: "216"
tags: [mktoon, blender]
---

# Lesson: Authoring Toon Control Maps — Ramp, Noise, Threshold (0018)

## RESCOPE (2026-08-28, after #220 code audit + spikes)

**Ramp SPLIT OUT to its own topic (#246).** The code audit found mk_toon_lite has NO
`diffuse_ramp` slot — the ramp is a different mechanism in `toon_ramp.gdshader`
(alternative banding, sibling of toon-banding), not a mk_toon_lite control map. This
lesson is now **noise + threshold only** — the two maps mk_toon_lite actually samples.
MAP updated: toon-control-maps retitled "Noise & Threshold", ramp-band-textures added
as a sibling node with prereq [toon-banding].

**Corrections to the arc below (ticket paraphrase was wrong — teach the shader AS IT IS):**
- Ignore all "ramp" / `diffuse_ramp` content in the arc below — that's #246 now.
- Noise + threshold are sampled in `light()`, NOT `fragment()`.
- Noise uniform is `noise_strength` (default 0.04, hint_range 0.0–0.25), NOT `noise_intensity=0.3`. Rewrite the exercise around the real range.
- Threshold has NO strength uniform — bias is fixed `texture(...).r - 0.5` (±0.5). The map's contrast IS the only control.
- `noise_scale`/`threshold_map_scale` are bare floats (no hint_range).
- Verbatim sampling code + wiring: see .scratch/subagent-raw/220-code-review.md §1.

**Oracle decision (spiked both; complementary, both first-class — see 220-spike-*.md,
pillow-mise-research.md, pillow-integration-code.md):**
TWO complementary checks, neither optional, neither able to do the other's job:
- **Sidecar oracle** (stdlib, in verify): bake script measures each map inside Blender
  (img.pixels) and writes a JSON sidecar; stdlib oracle asserts contracts including the
  things ONLY knowable at bake time — Non-Color intent, AO↔threshold correlation, level
  counts. (Pillow CANNOT read Non-Color intent from a PNG — no such flag exists.)
- **Pillow drift-check** (in verify, ImportError-guarded): reads the COMMITTED PNGs and
  asserts dims, channel mode, and tileability edge-diff match the sidecar's recorded
  values — catches a hand-edited/re-exported PNG that the sidecar (trusts last bake)
  would miss. Uses `with Image.open`, convert("RGBA") before compare (palette-mode P
  drops data), NumPy [y,x] axis order, edge slices a[0,:]/a[-1,:].

**Pillow incorporation (first-class, NOT `uv run --with`):** add `pillow` to the existing
`[tasks.setup]` inline `uv pip install ...` line (unpinned, house style — matches all 15
current deps). We have NO pyproject/uv.lock, so `uv add` is out of scope — migrating the
whole dep model to pyproject is a separate infra ticket. Add a `python -c "import PIL"`
canary to `[tasks.doctor]` Venv block. cp312 Windows wheel is prebuilt (no compiler).

**Verify wiring:** ... palette-snap-oracle.py, control-maps-oracle.py (sidecar, stdlib),
control-maps-drift.py (Pillow, guarded), verify-links.py, ...

**Tileable noise:** use the 4D-noise trick (map UV onto two orthogonal circles via
sin/cos into Blender's Noise Texture set to 4D) — edges match by construction. Verify
with a half-offset edge-match test (the sidecar's edge_max_diff ≈ 0).

**Threshold from AO:** Barrel_01 ARM R channel, read Non-Color; darker AO = earlier/deeper
shade. Canonical prior art: MToon shadingShiftTexture, UTS2 Shading Grade Map.

## Task 8 (Godot A/B) plan — CORRECTION from research (2026-08-28)

`--headless` CANNOT render 3D to PNG (dummy DisplayServer → blank framebuffer). Headless
is fine for IMPORT only. The Tier-3 visual A/B needs a real GPU/windowed run. Environment
supports it (Godot 4.7.1 on PATH, test-scene imported, prior barrel_with/without_shader.png
A/B pair proves it works). Plan (from .scratch/subagent-raw/220-godot-capture-review.md):
1. Copy baked PNGs to test-scene/assets/masks/, import (--headless --import ok), valid=true.
2. Crisp-band lighting CONSTANT (skill): light_bands=3, scale=0.9, wrapped=0.3, gooch=0.5,
   ¾ raking DirectionalLight3D — REQUIRED or the toggle rides on invisible band boundaries.
3. Capture BEFORE (maps off).
4. DISK-EDIT mktoon_test.tscn (barrel node MKToonTestScene/Barrel/Barrel_01, material
   SubResource ShaderMaterial_mktoon): add 2 Texture2D ext_resources + use_noise_map=true,
   noise_map=ExtResource, noise_strength=0.25, noise_scale=4.0, use_threshold_map=true,
   threshold_map=ExtResource, threshold_map_scale=1.0. NEVER runtime set_shader_parameter,
   NEVER MCP save_scene (both skill hard-rules — save_scene strips inline SubResources).
5. Capture AFTER.
6. Capture mechanism: dispatch the godot_editor SUBAGENT (default agent can't call the
   Godot MCP). It runs project_run → game_eval save_png → copy from app_userdata/screenshots.
7. INDEPENDENT validation (skill hard-rule #3, agent self-report unreliable): fresh image
   read against the research rubric — ON = band edges wobble organically (interior stays
   flat) + shadow deeper/earlier in creases (terminator still crisp); OFF = clean stripes.
8. git restore .tscn (or keep maps-on as demo); copy validated PNGs to lesson figure.

FALLBACK (windowed capture blocked AND MCP subagent unavailable): compile-only
(--headless --import confirms shader+PNG-referenced .tscn load, no errors) + LOG the visual
A/B as a deferred known gap (code-validation-teaching: compiles ≠ correct). Not silent.

Visual-correctness rubric (from 220-research-visual-effect.md): noise CORRECT = one coherent
wavy seam between still-flat bands (BROKEN = grain bleeding into band / speckle); threshold
CORRECT = shadow grows localized in creases, terminator crisp, convex faces ~unchanged
(BROKEN = uniform global darkening / light leak / wrong sign).

---

## What to build (ORIGINAL — see RESCOPE above; ramp content moved to #246)

A substantial lesson teaching how to create the toon-specific control textures that `mk_toon_lite.gdshader` expects but nobody provides. These maps don't replace albedo — they tell the shader HOW to shade.

### Lesson arc

1. Introduce the concept: control maps are artist instructions to the shader. They're small (ramp: 8×1, noise: 256×256 tileable, threshold: same res as albedo) and reusable across assets.
2. **Ramp texture** — create a 1D gradient (8×1 or 16×1 pixels) that defines the band-to-color mapping. Show how the shader samples it: `texture(diffuse_ramp, vec2(NdotL, 0.5))`. Design 3 ramp variants: hard-cel, soft-gradient, warm-to-cool (Gooch-like).
3. **Noise map** — create a tileable organic noise texture (Blender's noise texture node → bake). Show how the shader uses it: adds to NdotL before quantization, creating organic edge variation. Compare different noise frequencies.
4. **Threshold map** — extract from existing AO channel (ARM texture R channel from Poly Haven). Show how the shader uses it: per-pixel bias on the shadow boundary. Darker AO = earlier shadow. This gives "free" spatial shadow variation without hand-painting.
5. Demonstrate each map's visual effect independently (before/after toggling each slot)

### Key concept

> Control maps are small, cheap textures that give artists per-pixel authority over shader behavior. They don't define color — they define WHERE and HOW the shader applies its effects. One noise map + one ramp can transform a generic toon shader into a distinctive style.

### Code deliverables

- 3 ramp textures (8×1): hard-cel, soft-gradient, warm-cool
- 1 tileable noise map (256×256) baked from Blender procedural noise
- 1 threshold map derived from Barrel_01 ARM texture R channel
- Blender file showing the bake setup for each

### Exercise

"The mk_toon_lite shader has a `noise_intensity` uniform defaulting to 0.3. Predict: what happens if you set it to 0.0 vs 1.0 with the same noise map? Which gives the more 'hand-painted' look and why?"

## Acceptance criteria

- [ ] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/04-toon-control-maps.html`
- [ ] 3 ramp textures created and working with toon_ramp.gdshader
- [ ] Noise map created (tileable, 256×256) and demonstrated in mk_toon_lite
- [ ] Threshold map extracted from AO and demonstrated
- [ ] Each map shown independently with before/after
- [ ] Explains shader sampling code for each map type
- [ ] SR questions generated (3-5 cards)
- [ ] Reference files: actual texture assets in reference/code/toon-control-maps/

## Research context

**From MK.Toon requirements research:**

Toon-specific control maps (often tool-generated):
| Texture Slot | Purpose |
|-------------|---------|
| Ramp Texture (1D) | Defines light-to-dark band colors. MK.Toon includes a "Ramp Creator" tool. |
| Threshold Map | Per-pixel shading shift (like MToon's `shadingShiftTexture`) |
| Outline Width Map | Per-vertex outline control (grayscale) |

What's procedural vs authored:
- Procedural: banding, specular, rim, shadow color, outline = all computed in shader
- Authored: albedo, normal, shade color texture, ramp, threshold = artist provides

**From toon-texture-pipelines research:**

Guilty Gear ILM map channel packing:
- R: specular mask (which pixels reflect)
- G: shadow offset (light-independent painted shadows) ← this IS a threshold map
- B: specular size control
- A: inner line mask

MToon spec channel packing:
- R = shadingShiftTexture (threshold/shadow boundary shift)
- G = outlineWidthMultiplyTexture
- B = uvAnimationMaskTexture

**From existing-test-scene review:**

mk_toon_lite.gdshader uniform declarations (all EMPTY in scenes):
- `uniform sampler2D noise_map` — used in fragment() to bias NdotL before banding
- `uniform sampler2D diffuse_ramp` — alternative to floor-divide: texture lookup banding
- `uniform sampler2D threshold_map` — shifts shadow boundary per-pixel

ARM texture packing (Poly Haven): R=AO, G=Roughness, B=Metallic
- AO channel directly usable as threshold map base (darker = deeper shadow bias)
- Roughness/Metallic channels irrelevant (shader uses specular_disabled)

**From blender-bake-nodes research:**

For noise map baking:
- Use Blender's procedural Noise Texture node (type: fBM, scale ~4-8 for tileable)
- Connect to Emission shader → bake Emit pass at 256×256
- Set image to Non-Color data (it's a control map, not sRGB)
- Ensure tileability: use modulo UV or Blender's "Seamless" noise option (via Musgrave)
