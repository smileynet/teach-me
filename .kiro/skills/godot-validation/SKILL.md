---
name: godot-validation
description: "Validate shaders and capture visual A/B proof in the Godot test-scene project. Trigger: visual validation, shader validation, capture screenshots, A/B comparison, kuwahara test, godot screenshots, zoom to object, frame object, glTF import error, valid=false."
metadata:
  type: reference
  invocation: both
  practice: null
---

# Godot Visual Validation

Validate lesson shaders by applying them to PBR-textured meshes in `test-scene/` and capturing A/B screenshot proof.

## Test Scene

- Project: `D:\code\teach-me\test-scene`
- PBR assets: `test-scene/assets/polyhaven/` (Barrel_01, Camera_01, Lantern_01 — 1K textures)
- Shaders: `test-scene/shaders/` (copied from `examples/godot-gamedev/reference/code/`)
- Screenshot output: `test-scene/.scratch/screenshots/`

## glTF Import Fix

MCP `reimport`/`scan` do NOT trigger Godot's scene importer for glTF files. If `.gltf.import` shows `valid=false`:

1. Delete the `.gltf.import` files
2. Run `godot --headless --editor --import --quit --path test-scene`
3. Restart the editor (quit + relaunch)
4. Then `node_create` with `scene_path` will work

## Capturing Screenshots to Disk

`editor_screenshot` returns inline base64 only — cannot save to files. To get files:

1. Run the project (`project_run`)
2. Use `game_eval` to position camera, toggle shader, and save:

```gdscript
var img = get_viewport().get_texture().get_image()
img.save_png('user://screenshots/filename.png')
```

Files land at `C:/Users/uosmi/AppData/Roaming/Godot/app_userdata/teach-me-shader-test/screenshots/`. Copy to `test-scene/.scratch/screenshots/` after capture.

## Framing Objects (Fill the Frame)

Calculate camera distance from object AABB so it occupies ~80% of viewport:

```gdscript
var half_fov_tan = tan(cam.fov * 0.5 * PI / 180.0)
var dist = largest_aabb_dimension / half_fov_tan
```

Position camera at `target + offset` where offset uses 30° elevation/azimuth:

```gdscript
var elev = 30.0 * PI / 180.0
var azim = 30.0 * PI / 180.0
var offset = Vector3(dist * cos(elev) * sin(azim), dist * sin(elev), dist * cos(elev) * cos(azim))
cam.global_position = target + offset
cam.look_at(target)
```

## MCP Reliability (hard rules — validated 2026-08-26)

The godot-ai MCP has three failure modes that cause silent wrong results:

1. **`game_eval` mutations are for READING, not persisting.** Setting `rotation_degrees` or `set_shader_parameter` on a running instance is unreliable — changes may not affect the render or reset on the next `project_run`. Symptom: two different "edits" produce pixel-identical captures. Fix: edit the `.tscn` on disk (persistent, git-tracked), then `project_run` picks up saved state. Use `game_eval` only to capture the viewport and sample pixels.

2. **NEVER call MCP `save_scene` on a hand-authored `.tscn`.** It strips inline SubResources (ShaderMaterial), ext_resources, and `material_override` — reverting meshes to their default glTF material. Recover with `git restore`. Edit scene params via disk `strReplace` instead.

3. **The agent's visual self-report is UNRELIABLE.** It has claimed "crisp cel bands clearly visible" on an image that was actually flat uniform color. NEVER trust the capturing agent's description. Validate every capture with an independent read (fresh `kiro-cli chat --no-interactive` image analysis, or read the image yourself) AND sample pixels via `game_eval` for objective confirmation.

**Reliable capture loop:** edit `.tscn` on disk → `project_run` → `game_eval` (read-only viewport capture + pixel sample) → independent image validation → never `save_scene`.

## Shader Toggle for A/B

For post-process shaders, toggle `PostProcessRect.visible` in `game_eval` (this DOES work — it's a node visibility flag, not a persisted param):

```gdscript
var pr = get_tree().root.get_node('ColorTestScene/PostProcess/PostProcessRect')
pr.visible = false  # shader OFF
await get_tree().process_frame
await get_tree().process_frame
# capture here
pr.visible = true   # shader ON
```

For material_override shader PARAMETERS (per-object toon settings), edit the `.tscn` on disk between captures — runtime `set_shader_parameter` is unreliable (see MCP Reliability #1).

## GDScript Gotchas in game_eval

- `deg_to_radians()` does NOT exist. Use `angle * PI / 180.0`.
- Always `await get_tree().process_frame` (×2) after visual changes before capturing.
- Return values must be simple types (String, int, float) — not objects.

## Asset Rules

- **Never** use pixel-art (Kenney, KayKit) for color simplification testing — already flat-color, effect is invisible.
- **Always** use 1K+ PBR textures (Poly Haven CC0) for Kuwahara, posterize, palette snap validation.
