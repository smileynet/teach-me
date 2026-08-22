# Toon Outlines — Code Files

## Files

- **toon_outline.gdshader** — Inverted hull outline (per-object). Apply as `next_pass` on any existing toon material. View-space inflation keeps thickness consistent regardless of camera distance. Best for characters where you need per-object control.

- **toon_outline_screen.gdshader** — Screen-space edge detection outline (scene-wide). Apply to a fullscreen quad (QuadMesh 2×2, child of Camera3D). Detects both silhouettes AND internal edges via depth + normal discontinuities. Better visual quality, no mesh prep needed. Requires Forward+ or Mobile renderer.

## Setup: Inverted Hull

1. Select a mesh with a toon material (e.g., toon_bands)
2. In the material inspector, click Next Pass → New ShaderMaterial
3. Assign `toon_outline.gdshader`
4. Adjust `outline_width` (0.01–0.03 for characters)

## Setup: Screen-Space

1. Add a MeshInstance3D as child of Camera3D
2. Set mesh to QuadMesh, size (2, 2)
3. Set position to (0, 0, -1)
4. Assign ShaderMaterial with `toon_outline_screen.gdshader`
5. Set material Render Priority to 1
6. Adjust `depth_threshold` and `normal_threshold` for your scene
