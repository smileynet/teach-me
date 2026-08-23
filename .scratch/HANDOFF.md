---
created_at: 2026-08-23T07:25:00-07:00
base_commit: 5090808
handoff_key: toon-shader-lessons
---

# Handoff

## Objective
Godot Toon Shaders lesson track: visual A/B validation of color simplification shaders on PBR assets, proving the Kuwahara effect works on real textures.

## Constraints
- Shader validation = Godot runtime only (no regex linters).
- test-scene project at `D:\code\teach-me\test-scene`.
- Low-res pixel-art assets are UNSUITABLE for color simplification testing (proven A/B identical).
- Poly Haven 1K PBR textures are required for Kuwahara/posterization/palette testing.

## Prior Decisions
- Lessons 0003–0008 complete, all shaders compile clean in Godot 4.7.1.
- glTF import fix: delete stale `.import` files (with `valid=false`), then run `godot --headless --editor --import --quit` to force scene importer to generate `.scn` cache files. Editor restart required after.

## Current State
- **Poly Haven models instanced**: Barrel_01, Camera_01, Lantern_01 now live in `test-scene/scenes/color_test.tscn` with proper positions.
- **A/B screenshots captured** to `test-scene/.scratch/screenshots/` — 6 files (3 objects × with/without shader). Camera distance calculated from AABB: `dist = largest_dim / tan(fov/2)`.
- **Shader toggle method**: Set `/ColorTestScene/PostProcess/PostProcessRect` visibility to false/true via `game_eval`.
- **File sizes confirm effect**: shader-on PNGs are 10-20% smaller than shader-off (smoothing reduces entropy).
- Scene saved. No uncommitted lesson changes.

## Next Steps
1. **Review screenshots** at `test-scene/.scratch/screenshots/` — confirm Kuwahara effect is visually unmistakable on all 3 objects.
2. **Mark color-simplification as `complete`** in MAP.md once visually validated.
3. **Commit** the updated `color_test.tscn` (now has Poly Haven instances) and screenshot evidence.
4. **#183/#184 design decisions** (shared lesson library vs private lessons) — still unanswered.

## Fog
- The vintage camera and lantern are small props — screenshots at calculated distance may still show significant background. May need tighter FOV or closer distance for compelling A/B proof.
- Whether kernel_size=3 is dramatic enough for lesson screenshots (could bump to 5+ for more obvious effect).

## Evidence
- Screenshots: `test-scene/.scratch/screenshots/{barrel,camera,lantern}_{with,without}_shader.png`
- Prior session A/B proof (Kenney identical): `.scratch/reviews/codex-review.md`
- glTF import fix validated in this session (editor restart + headless import pipeline)

## Recommended Updates
- [ ] test-scene/README.md: document glTF import fix procedure (delete `.import` → headless import → restart)
- [ ] AGENTS.md: add glTF import troubleshooting to Constraints ("valid=false in .import files requires deletion + headless reimport")
