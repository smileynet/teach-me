# Toon Outlines — Code Files

## Files

- **toon_outline.gdshader** — Inverted hull outline (per-object). Apply as `next_pass` on any existing toon material. View-space inflation keeps thickness consistent regardless of camera distance. Best for characters where you need per-object control.

- **toon_outline_smooth.gdshader** — Inverted hull with smooth normals from vertex color. Same as above but reads extrusion direction from `COLOR.rgb` instead of `NORMAL`, fixing the disjointed outline on hard-edge geometry (cubes, swords). Requires smooth normals baked in Blender.

- **toon_outline_screen.gdshader** — Screen-space edge detection outline (scene-wide). Apply to a fullscreen quad (QuadMesh 2×2, child of Camera3D). Detects both silhouettes AND internal edges via depth + normal discontinuities. Better visual quality, no mesh prep needed. Requires Forward+ or Mobile renderer.

- **toon_outline_jfa_pass.gdshader** — JFA flood pass (educational reference). Shows the core algorithm: check 8 neighbors at a grid offset, keep the closest seed. Runs multiple times with halving offsets to build a distance field. For production use, install [pink-arcana/godot-distance-field-outlines](https://github.com/pink-arcana/godot-distance-field-outlines).

## Setup: Inverted Hull

1. Select a mesh with a toon material (e.g., toon_bands)
2. In the material inspector, click Next Pass → New ShaderMaterial
3. Assign `toon_outline.gdshader` (or `toon_outline_smooth.gdshader` for hard-edge meshes)
4. Adjust `outline_width` (0.01–0.03 for characters)

## Setup: Screen-Space

1. Add a MeshInstance3D as child of Camera3D
2. Set mesh to QuadMesh, size (2, 2)
3. Set position to (0, 0, -1)
4. Assign ShaderMaterial with `toon_outline_screen.gdshader`
5. Set material Render Priority to 1
6. Adjust `depth_threshold` and `normal_threshold` for your scene

## Setup: JFA (via addon)

1. Install [pink-arcana/godot-distance-field-outlines](https://github.com/pink-arcana/godot-distance-field-outlines) from GitHub
2. Add the DFOutlineNode (CanvasItem) or DFOutlineCE (CompositorEffect) to your scene
3. Configure outline width, color, and effects in the inspector
4. The addon handles multi-pass orchestration automatically
