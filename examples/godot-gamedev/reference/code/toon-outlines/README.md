# Toon Outlines — Code Files

## Files

- **toon_outline.gdshader** — View-space inverted hull outline shader. Apply as `next_pass` on any existing toon material. Inflates vertices in view space for consistent screen-space thickness regardless of camera distance.

## Usage

1. Select a mesh with a toon material (e.g., toon_bands)
2. In the material inspector, click Next Pass → New ShaderMaterial
3. Assign this shader
4. Adjust `outline_width` (0.01–0.03 for characters) and `outline_color`
