---
id: "253"
title: "Improve 0018 control-maps figure — isolated noise-only/threshold-only/both panels"
status: open
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

- [ ] 4-panel (or off + 3-effect) figure: off / noise-only / threshold-only / both
- [ ] Each isolated effect is independently legible (distinguishable without labels — verified by independent image read)
- [ ] noise panel shows band-seam wobble (interior flat); threshold panel shows deeper crease shadow (terminator crisp)
- [ ] Lesson 04-toon-control-maps.html figure + caption updated; caption honest to the visible effect
- [ ] verify-links green (new images resolve); mise run verify EXIT 0
