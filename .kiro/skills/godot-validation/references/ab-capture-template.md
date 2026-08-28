# A/B Capture Brief Template (godot_editor subagent)

Copy this into `.scratch/subagent-input/{ticket}-godot-ab-brief.md`, fill the blanks, and
dispatch the `godot_editor` subagent (the default agent can't call the Godot MCP). Distilled
from the #220 (control maps) and #221 (bake/export) captures — both succeeded first try.

The A/B is always: SAME scene + SAME shader + SAME lighting, ONE variable changed on disk.

---

## Verified facts (fill in — do NOT let the subagent rediscover)

- Scene: `test-scene/scenes/{scene}.tscn` (or "build one — no pre-wired scene exists")
- Mesh/node path: `{NodePath}`
- Shader: `res://shaders/{shader}.gdshader`; relevant uniforms: `{list them + types}`
- The ONE variable that changes between A and B: `{param or texture slot}`
  - BEFORE value: `{...}`
  - AFTER value: `{...}` (import any new texture first; confirm it's on disk)

## HARD RULES (from godot-validation SKILL.md — violating wastes the run)

1. Edit the `.tscn` ON DISK (strReplace), then `project_run`. NEVER runtime
   `set_shader_parameter` to toggle (two edits → identical captures). NEVER MCP `save_scene`
   (strips inline SubResources/material_override).
2. Capture via `project_run` + `game_eval`:
   `get_viewport().get_texture().get_image().save_png("user://screenshots/NAME.png")`.
   Copy from `%APPDATA%/Godot/app_userdata/{project}/screenshots/` to
   `test-scene/.scratch/screenshots/`.
3. `--headless` CANNOT render 3D (blank framebuffer) — use a REAL windowed `project_run`.
4. After a visual change: `await get_tree().process_frame` ×2 before capture.
5. Verify file existence with a direct filesystem stat, not `res://` resolution.

## Lighting CONSTANT (so the toggle is visible, not washed out)

Band-boundary effects need crisp bands + a raking light or they're invisible:
`light_bands ≈ 3–4`, `light_bands_scale ≈ 0.6–0.9`, ¾ side-raking DirectionalLight3D so the
terminator crosses the visible face. Frame the object to ~80%. Keep this identical A vs B.

## Steps

1. Set the lighting constant (disk edit).
2. Capture A (before) → `{name}-before.png`.
3. Disk-edit the ONE variable → B.
4. Capture B (after) → `{name}-after.png`.
5. Report the two ABSOLUTE paths + the exact .tscn diff applied. Do NOT judge the images —
   the parent validates independently. If windowed rendering is unavailable, SAY SO
   (do not fabricate).

## Parent's job (do NOT delegate — skill hard-rule 3)

- Read both PNGs yourself; confirm they're distinct (SHA256) and show the expected effect.
- Judge honestly — if the effect is subtle, write an honest caption; don't overclaim.
- Restore shared test infra (`git restore` the .tscn) or gitignore the throwaway A/B scene.
