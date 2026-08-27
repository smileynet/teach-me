# Blender Node Setups & Baking Workflows for Texture Simplification

## Summary

Blender provides several approaches to texture simplification through shader nodes: posterization via Math nodes (multiply → floor → divide), palette snapping using 1D texture lookups with Closest interpolation, and normal flattening through high-to-low-poly baking with controlled ray distance. The standard baking pipeline requires Cycles, a UV-unwrapped mesh, and an unconnected Image Texture node selected as the bake target. For toon/stylized workflows, EEVEE's Shader to RGB node enables real-time color ramping but cannot be baked directly — artists must either replicate the effect with Cycles-compatible nodes (Toon BSDF + Color Ramp) or bake via Emit pass with the stylized material connected to Material Output.

---

## 1. Posterization Node Setup (Shader Editor)

**Problem:** Reduce continuous gradients to discrete color bands (N steps).

### Method A: Math Floor (Most Common)

Node chain:
```
Image Texture → [Vector Math: Scale (factor=N)] → [Vector Math: Floor] → [Vector Math: Scale (factor=1/N)] → Base Color
```

Detailed breakdown (from BSE #304301):
1. **Multiply** the color channels by the number of desired steps (e.g., 8)
   - Colors now range 0–8 instead of 0–1
2. **Floor** to cut off decimal parts (0.245→0, 3.712→3)
3. **Divide** by the same step count to remap back to 0–1
4. Optionally add `0.5/N` offset to center each band

In Blender's Shader Editor, this uses:
- `Vector Math` node set to **Scale** (multiply all channels uniformly by N)
- `Vector Math` node set to **Floor**
- `Vector Math` node set to **Scale** (multiply by 1/N)

### Method B: Separate RGB + Greater Than (BSE #101750)

For hard-edge posterization with manual threshold control:
1. Separate RGB into individual channels
2. Each channel → Math node set to **Greater Than** with threshold from a shared Value node
3. Recombine with Combine RGB

**Source:** https://blender.stackexchange.com/questions/304301/posterize-node-in-material-shader
**Source:** https://blender.stackexchange.com/questions/101750/how-to-posterize-a-texture-in-cycles-proceduraly

---

## 2. Palette Snapping / Color Lookup

**Problem:** Map every pixel to the nearest color in a limited palette.

### Method A: 1D Palette Texture with Closest Interpolation

1. Create a small image (e.g., 5×1 or 8×1 pixels) where each pixel is a palette color
2. Use an Image Texture node set to **Closest** interpolation (not Linear)
3. Feed posterized grayscale or color channel as the UV coordinate lookup
4. The texture acts as a color lookup table (CLUT)

**Source:** https://blender.stackexchange.com/questions/222423/how-to-set-up-a-color-palette-in-blender

### Method B: Color Ramp with Constant Interpolation

1. Convert the texture to grayscale (RGB to BW node)
2. Feed into a **Color Ramp** with interpolation set to **Constant**
3. Place color stops at desired positions using your palette colors
4. This provides a direct mapping from luminance → palette color

### Method C: Dynamic Color Palette Add-on (DCP)

A Blender extension designed for stylized/low-poly game workflows:
- Generates an HSV color palette texture and a PBR data map
- All faces share one material; color determined by UV position in the palette
- One mesh, one material, one draw call in game engines
- Exports Godot 4 spatial shaders (`dcp_multicol.gdshader`, `dcp_singlecol.gdshader`)
- Supports runtime blending between two palette cells

**Source:** https://extensions.blender.org/add-ons/dynamic-color-palette/

### Method D: Nearest-Color Node Group (BSE #280223)

Community approach: build a node group that computes Euclidean distance in RGB space to each palette color and outputs the closest match. Requires OSL or a complex node tree with multiple Compare/Min operations — impractical for more than ~5 colors without scripting.

**Source:** https://blender.stackexchange.com/questions/280223/map-color-texture-to-closest-color-in-a-palette

---

## 3. Normal Map Flattening / Simplification

**Problem:** Produce simplified normals for stylized rendering (fewer surface details).

### Approach A: Flat-Shaded Low-Poly Bake

- Set low-poly mesh to **Flat Shading** (not Smooth)
- Bake normals with "Selected to Active" from high-poly
- Result: normal map only captures major form changes, not smooth interpolation
- The normal map compensates for the flat normals, giving a "faceted but detailed" look

### Approach B: Smooth Low-Poly with Intentionally Flat Normal Map

- If you want the result to look flat/simplified:
  - Bake from the SAME mesh to itself (no high-poly source)
  - Or use a flat purple (128, 128, 255) normal map = no perturbation
  - Combine with posterized base color for a cel-shaded look

### Approach C: Controlled Ray Distance

- Set **Max Ray Distance** low in Bake settings
- Rays that don't reach geometry produce flat (purple) results
- Use this deliberately to flatten distant/minor details while keeping major forms

### Key Settings for Normal Baking:
- **Render Engine:** Cycles
- **Bake Type:** Normal
- **Space:** Tangent (for deforming meshes) or Object (for static)
- **Selected to Active:** Enable for high-to-low transfer
- **Extrusion:** ~0.1 (small value to avoid overshooting)
- **Max Ray Distance:** Control how much detail transfers
- **Color Space:** Set to **Non-Color** BEFORE baking (locks after bake)
- **32-bit Float:** Recommended for normal maps

**Source:** https://blender.stackexchange.com/questions/215727/when-baking-normals-do-i-have-to-set-shading-to-smooth-or-flat-for-the-low-mesh
**Source:** https://docs.blender.org/manual/en/2.80/render/cycles/baking.html

---

## 4. Toon Shader Baking Workflows

### Workflow A: Toon BSDF → Bake Combined/Diffuse (Cycles)

1. Set up Toon BSDF shader in Cycles
2. Position key light to create desired shadow placement
3. Add unconnected Image Texture node (selected, UV-mapped)
4. Bake Type: **Combined** or **Diffuse** (with Direct + Indirect ON for baked lighting)
5. Result: flat texture with toon shading baked in
6. Apply baked texture via `MeshBasicMaterial` / unlit shader in game engine

**Source:** https://blender.stackexchange.com/questions/285478/blender-toon-bsdf-to-flat-texture

### Workflow B: EEVEE Shader to RGB → Reconstruct in Cycles for Bake

EEVEE's `Shader to RGB` node enables real-time toon effects but cannot be baked directly.

**Workaround:**
1. Design the look in EEVEE using Shader to RGB + Color Ramp
2. Switch to Cycles
3. Replace `Shader to RGB` with `Toon BSDF` + 0 ray bounces + sharp shadows (light angle = 0)
4. Route through Color Ramp for the same band effect
5. Bake as Combined or Emit

**Source:** https://blender.stackexchange.com/questions/344052/is-there-a-shader-to-rgb-alternative-for-cycles-rendering
**Source:** https://blender.stackexchange.com/questions/167017/toon-shading-light-direction

### Workflow C: Emit Pass Bake (Lighting-Independent)

For baking material color WITHOUT scene lighting:
1. Connect your stylized/posterized material to an **Emission** shader
2. Set Bake Type to **Emit**
3. Or: Bake Type = **Diffuse** with **Direct** and **Indirect** unchecked
4. Result: pure material color, no lighting influence

**Source:** https://blender.stackexchange.com/questions/165175/how-do-i-bake-my-texture-for-animation

### Workflow D: Combined Bake for Web (Medium article workflow)

From RJean Lee's EEVEE-to-Three.js pipeline:
1. Design stylized material in EEVEE (using Cycles-compatible nodes only)
2. Switch to Cycles for baking
3. Create Image Texture node → select it (don't connect)
4. Bake Type: **Combined**
5. Save baked image
6. Export model as .glb, apply baked texture as `MeshBasicMaterial` in Three.js

**Source:** https://yunchen-lee.medium.com/stylized-3d-model-for-the-web-blender-eevee-to-three-js-via-texture-baking-93e7200cda00

---

## 5. Bake Settings Reference

| Setting | Value | Notes |
|---------|-------|-------|
| Render Engine | Cycles | EEVEE cannot bake |
| Bake Type | Emit / Diffuse / Combined / Normal | Choose per-pass |
| Samples | Low (1-16) for flat shading | Higher for smooth gradients |
| Margin | 4-16 px | Prevents UV seam artifacts |
| Selected to Active | On for high→low transfer | Off for self-bake |
| Extrusion | 0.05-0.1 | For Selected to Active |
| Direct/Indirect | Off for color-only bake | On for baked lighting |
| Image Size | 1024-4096 px | Depends on UV efficiency |
| Color Space | Non-Color (normals), sRGB (color) | Set BEFORE baking |
| 32-bit Float | Yes for normals | No for color maps |

---

## 6. Add-on Recommendations

| Add-on | Purpose | URL |
|--------|---------|-----|
| **SimpleBake** (Blender Market) | One-click PBR baking, handles multi-material complexity | https://blendermarket.com/products/simplebake---simple-pbr-and-other-baking-in-blender-2/ |
| **SimpleBake** (free, GitHub) | Basic bake types (Emit, Normal, Shadow, AO) with auto-save | https://github.com/InamuraJIN/SimpleBake |
| **Dynamic Color Palette (DCP)** | UV-driven palette textures for low-poly/stylized workflows, Godot 4 shader export | https://extensions.blender.org/add-ons/dynamic-color-palette/ |
| **LSCherry Toon Shader** | Toon shader framework compatible with cross-toon materials | https://github.com/lvoxx/LSCherry |
| **btoon** | Simple toon material for EEVEE with rim lighting, SSS, specular | https://github.com/yuki-koyama/btoon |
| **One-Click Toon Converter** | Converts Principled BSDF → toon shader + outline automatically | https://tommywan622.gumroad.com/l/fmmjwl |
| **Dream Textures** | Stable Diffusion in Blender for AI-generated stylized textures | https://github.com/carson-katri/dream-textures |
| **Stylized Master Tools** | Pre-made stylized textures with one-click apply + bake | https://superhivemarket.com/products/stylized-master-tools/docs |

---

## 7. Complete Workflow: Posterized Texture with Palette Snapping

End-to-end pipeline for a stylized game asset:

1. **Model & UV unwrap** — Smart UV Project with small margin, maximize UV space
2. **Set up posterize nodes** — Multiply(N) → Floor → Divide(N) on base color
3. **Add Color Ramp** — Constant interpolation with palette colors at band positions
4. **Optional: palette texture lookup** — Feed posterized luminance into a 1×N palette image
5. **Flatten normals** — Either skip normals entirely (flat shading) or bake simplified normals from a beveled low-poly
6. **Prepare bake target** — Add unconnected Image Texture node, select it in all materials
7. **Bake Emit pass** — Captures material color without lighting
8. **Bake Normal pass** — If needed, with Tangent space and 32-bit float
9. **Save all images** — They are NOT auto-saved
10. **Export** — .glb with baked textures for game engine

---

## 8. Open Questions

- **Palette snapping at bake time vs runtime:** Baking with the palette lookup "freezes" the result — you can't change palette later. For games wanting runtime palette swaps, keep the palette texture separate and do the lookup in the game engine shader (like DCP does).
- **Normal map detail level:** There's no "detail slider" for normal baking. Control comes from mesh resolution (decimate before bake) or intentional blur on the normal map post-bake.
- **EEVEE baking future:** As of Blender 4.x, EEVEE still cannot bake. The Cycles workaround remains necessary.
- **Shader to RGB in Cycles:** Officially unsupported. The Toon BSDF + Color Ramp approach is the closest Cycles-native equivalent.

---

## Sources

1. https://blender.stackexchange.com/questions/304301/posterize-node-in-material-shader
2. https://blender.stackexchange.com/questions/101750/how-to-posterize-a-texture-in-cycles-proceduraly
3. https://blender.stackexchange.com/questions/280223/map-color-texture-to-closest-color-in-a-palette
4. https://blender.stackexchange.com/questions/285478/blender-toon-bsdf-to-flat-texture
5. https://blender.stackexchange.com/questions/267692/how-to-bake-a-texture-from-shader-nodes
6. https://blender.stackexchange.com/questions/215727/when-baking-normals-do-i-have-to-set-shading-to-smooth-or-flat-for-the-low-mesh
7. https://blender.stackexchange.com/questions/344052/is-there-a-shader-to-rgb-alternative-for-cycles-rendering
8. https://docs.blender.org/manual/en/4.0/compositing/types/filter/posterize.html
9. https://docs.blender.org/manual/en/2.80/render/cycles/baking.html
10. https://brandon3d.com/texture-baking/
11. https://extensions.blender.org/add-ons/dynamic-color-palette/
12. https://yunchen-lee.medium.com/stylized-3d-model-for-the-web-blender-eevee-to-three-js-via-texture-baking-93e7200cda00
13. https://github.com/InamuraJIN/SimpleBake
14. https://blendermarket.com/products/simplebake---simple-pbr-and-other-baking-in-blender-2/
15. https://github.com/lvoxx/LSCherry
16. https://github.com/yuki-koyama/btoon
17. https://github.com/carson-katri/dream-textures
18. https://blender.stackexchange.com/questions/222423/how-to-set-up-a-color-palette-in-blender
19. https://blender.stackexchange.com/questions/167017/toon-shading-light-direction
20. https://blenderartists.org/t/simplebake-simple-pbr-and-other-baking-in-blender/1186081/
