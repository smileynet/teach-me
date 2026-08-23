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

## Shader Toggle for A/B

Toggle via PostProcessRect visibility:

```gdscript
var pr = get_tree().root.get_node('ColorTestScene/PostProcess/PostProcessRect')
pr.visible = false  # shader OFF
await get_tree().process_frame
await get_tree().process_frame
# capture here
pr.visible = true   # shader ON
```

## GDScript Gotchas in game_eval

- `deg_to_radians()` does NOT exist. Use `angle * PI / 180.0`.
- Always `await get_tree().process_frame` (×2) after visual changes before capturing.
- Return values must be simple types (String, int, float) — not objects.

## Asset Rules

- **Never** use pixel-art (Kenney, KayKit) for color simplification testing — already flat-color, effect is invisible.
- **Always** use 1K+ PBR textures (Poly Haven CC0) for Kuwahara, posterize, palette snap validation.
