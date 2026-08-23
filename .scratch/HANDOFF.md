---
created_at: 2026-08-23T06:36:00-07:00
base_commit: c2490be
handoff_key: toon-shader-lessons
---

# Handoff

## Objective
Godot Toon Shaders lesson track: research-backed shader lessons with validated code, tested in a real Godot project against proper assets.

## Constraints
- Shader validation = Godot runtime only (no regex linters — ADR in `.kiro/steering/code-validation-teaching.md`).
- test-scene project at `D:\code\teach-me\test-scene` for compilation + visual validation.
- Low-res pixel-art assets (Kenney, KayKit) are UNSUITABLE for color simplification testing — they're already "simplified" by design.
- Poly Haven 1K PBR textures are the correct choice for Kuwahara/posterization/palette testing.
- `codex exec --dangerously-bypass-approvals-and-sandbox` required for Codex dispatch (updated in crew-research + deployed).

## Prior Decisions
- Lesson split: 0006 (hull + Sobel fundamentals) → 0007 (dual-viewport + JFA advanced). Codex-reviewed.
- Lesson 0008 (Color Simplification) complete: posterize in fragment() vs post-process, palette snap, Kuwahara.
- ADR 0008: component abstraction strategy (flowchart, bright lines, rule of three).
- Ticket #173 (CodeBlockToolbar) DONE — all 9/9 AC checked.
- Ticket #182 (shader validation) DONE — resolved as "use Godot runtime."
- Tickets #183/#184 (shared lesson library + private lessons) created as high-priority architectural tickets.

## Current State
- **Lessons 0003–0008 complete**, all passing linter, all shaders compile in Godot 4.7.1 headless.
- **test-scene has 15 shaders**, 28 low-poly models (Kenney/KayKit/Quaternius), 3 Poly Haven models (Barrel_01, Camera_01, Lantern_01) with 1K PBR textures downloaded + importing clean.
- **Visual validation gap**: color_test.tscn uses Kenney pixel-art textures which DON'T show Kuwahara effect (A/B screenshot proved identical). Poly Haven models downloaded but NOT yet instanced into a scene.
- **MAP.md** up to date: toon-outlines, advanced-outlines (complete), color-simplification (in-progress).

## Next Steps
1. **Instance Poly Haven models into color_test.tscn** — replace/supplement Kenney assets with Barrel_01/Camera_01/Lantern_01. These are glTF format (not GLB), located at `test-scene/assets/polyhaven/{model_name}/`.
2. **Visual A/B validation** — screenshot without shader, then with Kuwahara (kernel_size=5+). The effect MUST be unmistakable on 1K textures.
3. **Update MAP.md** — mark color-simplification as `complete` once visually validated.
4. **#183 design questions** — shared lesson library architecture (still unanswered from earlier session).
5. **Consider**: Poly Haven API (`api.polyhaven.com/assets?type=models`) for more test assets if needed.

## Fog
- Poly Haven glTF models may need manual scene instantiation (they imported as resources, not PackedScene). The `filesystem_manage(op="search", type="PackedScene")` returned empty — may need to open in editor GUI first.
- #183/#184 design questions unanswered: SR card definition shared vs local, completion semantics, map integration for private lessons.

## Evidence
- Linter: `check-lesson.py --workspace examples/godot-gamedev --all` → all pass
- Headless validation: `godot --headless --import --quit --path test-scene` → 0 errors (15 shaders + all assets)
- A/B screenshots: Kenney truck with/without Kuwahara = identical (proves pixel-art unsuitable)
- Codex review: `.scratch/reviews/codex-review.md` — 5 findings all addressed
- Research: `.scratch/research/` contains highres-texture-assets.md, kaykit-texture-analysis.md

## Recommended Updates
- [ ] .tickets/new: "Visual validation with Poly Haven PBR assets" — instance models, run A/B, capture proof
- [ ] AGENTS.md: add Poly Haven API as asset source (`api.polyhaven.com`, CC0, 1K-8K PBR textures)
- [ ] test-scene/README.md: document that color simplification testing requires Poly Haven assets (not pixel-art)
