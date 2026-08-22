# Advanced Outlines — Code Files

## Files

- **toon_outline_colorid.gdshader** — Spatial shader that branches on `CAMERA_VISIBLE_LAYERS`. Renders normal color for the main camera and a flat ID color for the outline camera. Apply to every mesh that should participate in per-object outlines.

- **toon_outline_colorid_detect.gdshader** — Canvas_item shader for edge detection on the color-ID viewport. Samples 8 neighbors and detects color boundaries. Apply to a TextureRect displaying the outline SubViewport's texture.

- **toon_outline_jfa_pass.gdshader** — JFA flood pass (educational reference). Shows the core algorithm: check 8 neighbors at a grid offset, keep the closest seed. For production, install [pink-arcana/godot-distance-field-outlines](https://github.com/pink-arcana/godot-distance-field-outlines).

## Setup: Dual-Viewport Color-ID

1. Create two SubViewports (MainViewport and OutlineViewport) with SubViewportContainers
2. Add Camera3D to each viewport:
   - Main camera: `cull_mask` includes layer 1, excludes layer 5
   - Outline camera: `cull_mask` includes layer 5, excludes layer 1
3. Set all meshes to `layers` = 1 + 5 (both layers)
4. Apply `toon_outline_colorid.gdshader` to each mesh — set `original_color` and a unique `outline_color`
5. Add a CanvasLayer with two TextureRect nodes displaying each viewport
6. Apply `toon_outline_colorid_detect.gdshader` to the outline TextureRect
7. Sync cameras via RemoteTransform3D (main camera → outline camera)

## Setup: JFA (via addon)

1. Install [pink-arcana/godot-distance-field-outlines](https://github.com/pink-arcana/godot-distance-field-outlines)
2. Add DFOutlineNode (CanvasItem) or DFOutlineCE (CompositorEffect) to your scene
3. Configure width, color, and effects in the inspector
4. The addon handles multi-pass orchestration automatically
