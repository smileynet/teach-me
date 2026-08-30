# Color Simplification — Code Files

## Files

- **posterize_albedo.gdshader** — Fragment-level posterization with toon banding. Spatial shader that reduces ALBEDO to N color levels before `light()` applies toon bands. Apply directly to meshes as their material.

- **posterize_screen.gdshader** — Post-process posterization with optional Bayer dithering. Canvas_item shader that reduces the final rendered frame to N color levels. Apply to a fullscreen ColorRect in a CanvasLayer.

- **palette_snap.gdshader** — Oklab perceptual palette snapping. Canvas_item shader that maps every pixel to the nearest color in an artist-defined palette using perceptually accurate distance. Apply to a fullscreen ColorRect.

- **kuwahara_basic.gdshader** — Basic 4-quadrant Kuwahara filter. Canvas_item shader that smooths texture detail while preserving edges, creating a painted look. Apply to a fullscreen ColorRect.

## Setup: Per-Material Posterization (posterize_albedo)

1. Create a new ShaderMaterial on a mesh
2. Assign `posterize_albedo.gdshader`
3. Set `albedo_texture` to the mesh's texture
4. Adjust `color_levels` (4 = aggressive, 8 = subtle)
5. Adjust `shadow_bands` for toon lighting

## Setup: Post-Process Effects (posterize_screen, palette_snap, kuwahara_basic)

1. Add a CanvasLayer to your scene (Layer = 1 or higher)
2. Add a ColorRect child (set to fullscreen: Layout → Full Rect)
3. Assign a new ShaderMaterial with the desired shader
4. Configure uniforms in the Inspector (levels, palette colors, kernel size)

## Stacking Multiple Effects

Apply multiple ColorRects in the same CanvasLayer — they process in tree order:
- Kuwahara first (smooth textures into flat regions)
- Posterize after (reduce the smoothed result to discrete bands)
- Or: Palette snap instead of posterize (art-directed color set)
