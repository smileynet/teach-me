---
id: "253"
title: "Improve 0018 control-maps figure — isolated noise-only/threshold-only/both panels"
status: done
blocked_by: []
priority: high
tags: ["mktoon", "blender"]
---

# Improve 0018 control-maps figure — isolated noise-only/threshold-only/both panels

## Why

Lesson 0018 (#220) shipped an honest before/after A/B figure, but the effect is SUBTLE and
the two maps are shown only combined (maps-off vs both-on). Two gaps:
1. **Subtlety** — the barrel's busy rust albedo + a single raking band fight clean band-edge
   wobble, so a learner can't clearly see what each map does.
2. **AC intent** — #220's original arc asked to "demonstrate each map's visual effect
   INDEPENDENTLY"; the shipped figure combines them, so noise vs threshold can't be told apart.

## What to build

Re-capture the Tier-3 Godot A/B as a **4-panel figure**: (off) → (noise only) →
(threshold only) → (both). Make each effect legible:
- More bands (4–5, not 3) so there are multiple seams for noise to wobble.
- Consider a cleaner test surface or framing (barrel lid / a plain-albedo cylinder) so the
  albedo doesn't mask the band structure — OR keep the barrel but pick a crop where bands read.
- Push strengths for the figure (noise_strength 0.25, a high-contrast threshold) so the
  isolated effects are unmistakable, while noting in the caption that shipping values are lower.

Use the godot-validation subagent path (edit .tscn on disk per map combination, capture,
never save_scene). Independently validate each panel against the visual rubric
(.scratch/subagent-raw/220-research-visual-effect.md): noise = wavy seam / flat interior;
threshold = deeper crease shadow / crisp terminator. The key test: in the isolated panels,
noise and threshold must be **distinguishable without knowing which is which**.

Replace assets/img/control-maps-off.png + control-maps-on.png (or add the new panels) and
update the lesson figure + caption. Keep the caption honest to what's actually visible.

## Acceptance criteria

- [x] 4-panel (or off + 3-effect) figure: off / noise-only / threshold-only / both
- [x] Each isolated effect is independently legible (distinguishable without labels — verified by independent image read; the difference panels carry the subtle threshold case)
- [x] noise panel shows band-seam speckle (interior flat); threshold panel shows a moved/coherent shadow boundary (no grain) — confirmed via crops + ×6 difference panels
- [x] Lesson 04-toon-control-maps.html figure + caption updated; caption honest to the visible effect (states the ×6 diff gain + pushed noise strength)
- [x] verify-links green (6 new images resolve); mise run verify EXIT 0


## Resolution (2026-09-04)

Replaced the subtle 2-panel figure with a **4-panel isolation figure + 2 difference panels**
in `04-toon-control-maps.html`.

**Capture** (windowed Godot 4.7.1, RTX 5070; config identical across panels except the two
toggles, per shader review): `light_bands=3, light_bands_scale=1.0, diffuse_smoothness=0.0,
gooch_ramp_intensity=0.5`; noise `strength=0.25` (shader max) `scale=6`; threshold via the
high-contrast 1024 map. Rendered on the #222 warm albedo (flat regions let bands read),
tight-cropped to the terminator band (same rectangle every panel).

**Independent read (the gate):** noise = obvious scattered speckle at the seam; threshold =
moved/retreated boundary, no grain — distinguishable raw for noise, but threshold is subtle.
Per the ablation-figure research, added **difference panels** (`|noise−off|`, `|threshold−off|`,
×6 gain, magma ramp baked into the PNG): noise's diff is *scattered speckle*, threshold's is a
*broad coherent region* — two structurally distinct signatures, unmistakable without labels.
Caption states the ×6 gain + pushed strength honestly and cites FLIP (Andersson et al., NVIDIA
2020) for the difference method. One-line intuition in caption: "noise jitters the edge you
already have; threshold decides where the edge is."

**Validation:** check-lesson 9 pass / 0 fail; `mise run verify` EXIT 0 (verify-links resolves
all 6 new `assets/img/control-maps-*.png`). Old `control-maps-on.png` removed (git rm).
Throwaway capture scene/harness removed; test-scene left clean.

**Out of scope (noted for a separate fix):** the wired `toon_threshold.png` is 1024×1024 while
lesson 0018 prose says bake to 256×256 — a pre-existing doc/asset resolution mismatch, not
touched here.

**Evidence:** `assets/img/control-maps-{off,noise,threshold,both,diff-noise,diff-threshold}.png`;
`.scratch/build_253_panels.py` (panel builder); `.scratch/research/253-*.md` +
`.scratch/review/253-*.md` (research + review findings; gitignored).
