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

4. **Verify file existence with a direct filesystem check, not `res://` resolution.** A capture agent (#220, 2026-08-28) reported source PNGs "missing on disk" because a `res://` path failed to resolve — the files were actually present (Godot was loading them fine from the `.ctex` cache). A `res://` lookup failure ≠ file absent. Before reporting a file missing, stat the real OS path. The parent must not act on a subagent's "missing file" claim without a direct check.

5. **`--headless` CANNOT render 3D to PNG.** Under `--headless` the DisplayServer is a dummy driver with no framebuffer — `get_viewport().get_texture().get_image()` returns blank/black (Blender/Godot parallel; validated #221, 2026-08-28). Headless is only for import/compile validation. A visual A/B capture needs a REAL windowed `project_run` (GPU). Reserve `--headless --editor --import --quit` for "does it load without errors" (Tier-3a); use the windowed `godot_editor` MCP path for pixels (Tier-3b).

## Headless GDScript validation (hard rules — validated 2026-08-28, #249/#236)

For running/validating GDScript headlessly (e.g. `mise run ink:validate-gd`):

1. **`godot --headless --editor --import --quit` returns exit 0 even on GDScript parse errors.** Do NOT trust its exit code. A broken script that's only `load()`ed by a scene (not an autoload/`class_name`/`@tool`) doesn't even error at import — it errors at scene-instantiation during the run. Validate by running the scene and matching `line.startswith(("SCRIPT ERROR", "ERROR: Failed to load script"))` on stderr → treat as a setup failure. **Anchor on the line prefix, not a free `"Parse Error"` substring** — interpolated content (story text, labels) can contain those words and false-trip a substring match.

2. **Cold `.godot/` cache emits benign parse-error noise on first import** (`SCRIPT ERROR: Parse Error: Could not preload ... icon.svg` from icon-bearing plugins like inkgd). **Double-import** (run `--import` twice) to warm the cache so the guarded run is clean.

3. **When a harness runs COPIES of shipped files, edit the SHIPPED reference, not the copy.** `tools/ink-gd-sync.py` regenerates `ink-test-project/scenes/lesson0*_player.gd` from `examples/ink-godot/reference/code/*/story_player.gd` on each run — hand-edits to the copies are overwritten.

## Shader Toggle for A/B

> For a full before/after capture via subagent, copy [references/ab-capture-template.md](./references/ab-capture-template.md) into `.scratch/subagent-input/` and dispatch `godot_editor` (validated first-try on #220 + #221).

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

## mk_toon_lite: gooch IS the band-color ramp (validated 2026-08-27)

In `mk_toon_lite.gdshader`, discrete light bands only render as **distinct colors** when `gooch_ramp_intensity > 0`. The band math computes a `lit_factor`, but the final color is `mix(shadow_color, lit_color, lit_factor)` — and with `gooch_ramp_intensity = 0`, `shadow_color == lit_color == ALBEDO`, so every band collapses to identical albedo (flat, no visible banding). Turning gooch OFF to "isolate pure banding" produces a flat single tone — the opposite of intent. **To show crisp bands: keep `gooch_ramp_intensity ≈ 0.5`, set `light_bands = 3`, `light_bands_scale ≈ 0.9`, and a moderate `wrapped_lighting ≈ 0.3`.**

Crisp-band capture recipe (barrel/cylinder, confirmed via pixel-row + image read):
- **¾ side-raking directional light** so the terminator crosses the visible front face (`N·L` sweeps 1→0 left-to-right). Front lighting → one flat band. Compute the light basis from a target travel direction via look_at math; a directional light emits along `-basis.z`.
- **Keep the cylinder** — a sphere's omnidirectional normals hide front-face washout (the real failure mode). The cylinder is the honest test mesh.
- Result: 3 clean vertical band stripes (e.g. `(255,181,71)` → `(235,141,56)` → `(116,76,36)`).
