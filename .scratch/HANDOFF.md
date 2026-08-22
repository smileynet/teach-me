---
created_at: 2026-08-22T07:52:00-07:00
base_commit: 82d1c22
handoff_key: toon-shader-lessons
---

# Handoff

## Objective
Godot Toon Shaders lesson track: research-backed shader lessons with validated code, tested in a real Godot project.

## Constraints
- Shader validation = Godot runtime only. No homebrewed linters (tried and deleted validate-shaders.py — false confidence).
- test-scene project at `D:\code\teach-me\test-scene` for compilation checks; `D:\code\gdhelper-pipeline\test-scene` for visual validation on real meshes.
- tkt: use `D:\code\tkt\target\release\tkt.exe` directly (mise shim recursion).
- `cull_disabled` required for triplanar on open geometry (sidewalks, roads).
- ATTENUATION includes shadow state (0–1), not just distance.

## Prior Decisions
- Callout hierarchy: 6 types (key-concept, decision, new-concept, comparison, gotcha, FYI). Decision callouts MUST include when-to-use + default. Enforced by Q14 in check-lesson.py.
- Code validation steering: use the learner's runtime, not regex linters. Visual confirmation non-negotiable for shaders.
- Outline lesson teaches both inverted hull (per-object) AND screen-space depth+normal (production quality). Industry pattern: combine both.

## Current State
- **Lessons complete:** 0001–0006. Lesson 0006 (Toon Outlines) generated with both approaches but NOT yet validated in Godot.
- **MAP.md outdated:** 0005 still shows `in-progress`, 0006 not added yet.
- **test-scene created:** `test-scene/` in teach-me repo with all 7 shaders + godot_ai MCP addon. Not yet opened/validated.
- **#173 still in-progress:** CodeBlockToolbar JS component (CSS done, JS remaining).
- **#182 open:** Shader validation tooling — may descope now that approach is "use Godot runtime."

## Next Steps
1. **Validate lesson 0006 shaders** — open test-scene in Godot, apply toon_outline.gdshader as next_pass and toon_outline_screen.gdshader on a fullscreen quad. Visually confirm.
2. **Update MAP.md** — mark 0005 complete, add 0006 toon-outlines topic.
3. **#173 CodeBlockToolbar** — build the JS component (copy + download buttons), mount in page-shell.js.
4. **Descope #182** — close with "resolved: use Godot runtime, not custom tooling."
5. **#181** — regression tests for Codex review F1–F4 fixes, dispatch fresh review.

## Fog
- Screen-space outline shader not yet tested in Godot — may need `depth_test_disabled` tweaks for 4.7.
- Outline lesson exercise references "smooth normals in Blender" — learner may not have Blender workflow. Consider whether to add a Blender sidebar or keep it as a mention.

## Evidence
- Linter: `check-lesson.py --workspace examples/godot-gamedev --all` → 6/6 pass
- Shaders in test-scene: `test-scene/shaders/` (7 files: toon_test, toon_bands, toon_ramp, toon_smoothstep, triplanar_toon, toon_outline, toon_outline_screen)
- Research: consumed and deleted from .scratch/ — findings applied to lessons and steering
