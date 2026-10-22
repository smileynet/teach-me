# MK.Toon & Toon Shader Texture Requirements

## Summary

MK.Toon (Unity) and similar toon shader systems (Unity Toon Shader/UTS, MToon) accept standard PBR texture inputs (albedo, normal, emission) but **procedurally generate the toon shading response** — they compute light bands, specular thresholding, and rim effects in the shader using math (step/smoothstep functions or ramp texture lookups). The textures they expect are largely the same as standard shaders (authored albedo, optional normal maps), while the stylization itself comes from shader parameters and optional 1D ramp textures. This is the key distinction: toon shaders don't need differently-authored base textures — they need standard textures plus toon-specific control maps.

## Texture Maps Used by MK.Toon

Based on the feature list from the Unity Asset Store and third-party documentation:

### Authored (Artist Must Provide)

| Texture Slot | Purpose | Notes |
|-------------|---------|-------|
| **Albedo Map** | Base color/diffuse | Standard RGB texture. Vertex colors used if no albedo is set. |
| **Normal Map** | Surface detail bumps | "Seamlessly integrated normal mapping into the stylized lighting" |
| **Emission Map** | Self-illuminating areas | Standard emission texture |
| **Detail Map** | Second layer atop albedo | Additive, multiplied, or mixed blend modes; detail normals also supported |
| **Occlusion Map** | Two-way occlusion | Controls direct AND indirect light occlusion separately |
| **Dissolve Pattern** | Dissolve mask | Grayscale pattern for dissolve effect |
| **Artistic Pattern** | Hatching/sketch/drawn texture | For "Artistic" modes; projected in tangent or screen space |

### Toon-Specific Control Maps (Often Generated via Tools)

| Texture Slot | Purpose | Notes |
|-------------|---------|-------|
| **Ramp Texture (1D)** | Defines light-to-dark bands | MK.Toon includes a "Ramp Creator" tool to generate these from a gradient. Alternative to Cel/Banded modes. |
| **Threshold Map** | Per-pixel shading shift | Like MToon's `shadingShiftTexture` — shifts where the light/shadow boundary falls per-texel |
| **Outline Width Map** | Per-vertex outline control | Grayscale: thinner outlines around eyes/delicate areas |
| **Iridescence Map** | View-angle color shift | Angle-dependent color effect |

### MK.Toon Included Tools (Generate Textures)

- **Ramp Creator**: Create 1D gradient ramp textures from a color gradient editor
- **Texture Channel Packer**: Combine R/G/B/A channels from different textures into one (for mask packing)
- **Mesh Utility**: Create meshes with smoothed normals for better outlines (not a texture, but relevant)

## What's Generated Procedurally vs Authored

### Procedural (computed in shader at runtime)

| Effect | Method |
|--------|--------|
| **Light banding (cel shading)** | `step()` or `smoothstep()` on NdotL; number of bands controlled by parameters |
| **Specular highlights** | Blinn-Phong half-vector dot thresholded with smoothstep |
| **Rim lighting** | Fresnel (1 - NdotV) thresholded |
| **Shadow color** | Lerp between lit color and shade color based on light threshold |
| **Outline** | Vertex extrusion along smoothed normals (in a separate pass) |
| **Gooch shading** | Interpolation between warm/dark colors based on lighting condition |
| **Light Transmission** | Subsurface/translucent pass-through |
| **Color Grading** | Contrast, saturation, brightness adjustment |

### Authored (artist provides)

| Artifact | Why it can't be procedural |
|----------|---------------------------|
| **Albedo** | Content-specific color information |
| **Normal map** | Content-specific surface detail |
| **Shade color texture** (in UTS/MToon) | A separate albedo for shadowed areas — can have different hue, not just darker |
| **MatCap texture** | Baked lighting sphere for hair luster etc. |
| **Ramp texture** | While generatable from tools, artists often hand-paint these for specific looks |
| **Outline width map** | Requires per-mesh artistic judgment (thin near eyes, thick on silhouette) |

## Unity Toon Shader (UTS) Specifics

UTS uses a **three-color-map** system:
1. **Base Map** — fully lit regions
2. **1st Shading Map** — lighter shadow regions
3. **2nd Shading Map** — darker shadow regions

These are THREE separate authored textures (not one albedo with procedural darkening). The shader selects between them based on NdotL thresholds controlled by `Base Color Step` and `Base Shading Feather` parameters.

Additional UTS textures:
- **MatCap Map** — view-space-normal-mapped sphere for hair/metallic luster
- **Outline Width Map** — per-vertex outline control
- **Angel Ring** — specialized hair highlight

## MToon (VRM Standard) Texture Slots

From the VRMC_materials_mtoon-1.0 specification:

| Property | Channel Used | Purpose |
|----------|-------------|---------|
| `baseColorTexture` (glTF core) | RGB | Lit color |
| `shadeMultiplyTexture` | RGB (sRGB) | Shade color multiplier |
| `shadingShiftTexture` | R (linear) | Per-pixel shading boundary shift |
| `normalTexture` (glTF core) | RGB | Surface normals |
| `emissiveTexture` (glTF core) | RGB | Emission |
| `matcapTexture` | RGB (sRGB) | MatCap sphere |
| `rimMultiplyTexture` | RGB (sRGB) | Rim lighting mask |
| `outlineWidthMultiplyTexture` | G (linear) | Outline width mask |
| `uvAnimationMaskTexture` | B (linear) | UV animation mask |

**Channel packing note:** MToon packs multiple masks into one texture:
- R = shadingShiftTexture
- G = outlineWidthMultiplyTexture  
- B = uvAnimationMaskTexture

## Esoteric Ebb Art Pipeline (for comparison)

Esoteric Ebb uses a unique approach that differs significantly from typical toon shader setups:
- 3D models are UV-mapped from the **fixed isometric camera perspective**
- A single large texture (4K–16K depending on area size) is hand-painted and applied on top
- The rendering is from a **fixed camera**, so textures can be painted to look correct only from that angle
- The color palette was created by Gibbet Games while modeling
- Real-time lighting is applied on top of the hand-painted textures

This is closer to a **pre-rendered background** approach than a traditional toon shader pipeline. The "toon" look comes from the hand-painted art style in the textures themselves, not from shader-based cel shading.

## Comparison: MK.Toon (Unity) vs Our Godot Port

| Aspect | MK.Toon (Unity) | Godot Toon Shader Port |
|--------|-----------------|----------------------|
| **Base input** | Standard albedo texture + PBR properties (metallic, roughness) as input, stylized output | Standard albedo + Godot spatial shader uniforms |
| **Light banding** | Four modes: Builtin, Cel, Banded, Ramp | Typically step/smoothstep on NdotL; ramp texture sampled via 1D texture |
| **Shade color** | Can use separate shade color/texture OR just darken albedo | Usually single shade color uniform (no separate shade texture in basic ports) |
| **Normal maps** | Full integration, doesn't break toon bands | Supported but can soften band edges (common gotcha — need to quantize AFTER normal perturbation) |
| **Ramp textures** | 1D gradient texture with built-in creator tool | `sampler2D` uniform, artist provides or generates manually |
| **Outline** | Three modes (mesh extrusion with smoothed normals); outline width map | Separate pass or inverted hull technique; Godot requires multi-pass via shader or second mesh |
| **Artistic modes** | Drawn, Sketch, Hatching (screen/tangent space) | Not standard — would need custom implementation |
| **MatCap** | Built-in | Can implement via view-space normal → UV lookup |
| **Gooch** | Built-in (warm/cool interpolation) | Would need custom implementation |
| **Channel packing** | Included tool packs R/G/B/A from different sources | Manual or via external tool |
| **Multi-pass** | Handled transparently by shader variants | Requires explicit `next_pass` in Godot materials |

### Key Implication for Our Godot Port

The most important texture requirement difference: **toon shaders don't need special textures** — they need standard PBR textures and then the shader controls how those textures are displayed under lighting. The procedural part (banding, ramp lookup, outline) is all in the shader math.

What our Godot port SHOULD expect from artists:
1. Standard albedo texture (same as any 3D model)
2. Optional normal map (with awareness that it softens toon band edges)
3. A 1D ramp texture (can be generated) OR shader parameters for band count/thresholds
4. Optional: shade color override (flat color or texture for shadow regions)
5. Optional: outline width map (grayscale, for per-vertex outline control)
6. Optional: MatCap sphere texture (for hair/metallic luster effects)

What the shader generates procedurally:
- All toon band computation
- Specular thresholding
- Rim/fresnel effects
- Outline geometry
- Shadow color interpolation

## Sources

- Unity Asset Store — MK Toon - Stylized Shader: https://assetstore.unity.com/packages/vfx/shaders/mk-toon-stylized-shader-178415
- Unity Toon Shader (UTS) Getting Started: https://docs.unity3d.com/Packages/com.unity.toonshader@0.12/manual/GettingStarted.html
- VRMC_materials_mtoon-1.0 Specification: https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_materials_mtoon-1.0/README.md
- Roystan Toon Shader Tutorial: https://roystan.net/articles/toon-shader/
- Toon Shaders in Unity (Medium): https://medium.com/@chitranshnishad27/toon-shaders-in-unity-from-shader-graph-to-custom-hlsl-08252b2d64a2
- 80.lv Esoteric Ebb Art Pipeline: https://80.lv/articles/check-out-these-beautiful-hand-painted-backgrounds-for-d-d-inspired-rpg
- Unity Toon Ramp Surface Shader: https://docs.unity3d.com/6000.2/Documentation/Manual/SL-SurfaceShaderExamples-ToonRamp.html
- unityassetcollection.com MK Toon feature list: https://unityassetcollection.com/mk-toon-stylized-shader-free-down1load/

## Open Questions

- MK.Toon's exact "Threshold Map" implementation details are behind the paid asset — we're inferring from MToon's equivalent (`shadingShiftTexture`)
- Whether MK.Toon uses separate shade textures (like UTS's 3-map system) or just shade colors is not confirmed from public docs
- The Esoteric Ebb team's specific shader setup within Unity (whether they use MK.Toon or a custom shader) has not been publicly documented — the 80.lv article describes the texture approach but not the shader system
