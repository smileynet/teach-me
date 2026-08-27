# Toon Texture Pipelines: PBR to NPR Conversion

## Summary

Converting PBR textures to toon-friendly textures involves three main strategies: (1) channel-packing custom control maps (ILM/SSS maps) as pioneered by Arc System Works, (2) baking stylized shader results back into flat textures via Blender's Cycles bake, and (3) real-time shader techniques that posterize/quantize PBR inputs at render time without rebaking. The industry standard for AAA toon rendering (Guilty Gear, Genshin Impact) does NOT convert PBR textures — it uses purpose-built hand-painted textures from the start, with custom channel-packed maps controlling shadow shape, specular behavior, and inner lines.

---

## Detailed Findings by Source

### 1. Guilty Gear Xrd — Arc System Works (GDC 2015)

**Source:** GDC 2015 talk "GuiltyGearXrd's Art Style: The X Factor Between 2D and 3D" by Junya C. Motomura

**Key technique:** Single texture with packed channels replaces the entire PBR texture set:
- **RGB:** Base color (hand-painted diffuse — NOT derived from PBR albedo)
- **Alpha channel:** Inner lines (drawn directly into the texture, not edge-detection)
- **Separate "ILM" (Illumination) Map** with packed channels:
  - **R channel:** Specular mask (which pixels reflect)
  - **G channel:** Shadow offset (light-independent painted shadows)
  - **B channel:** Specular size control (darker = larger specular)
  - **A channel:** Inner line mask (all-0 alpha = inner line pixel)
- **SSS Map:** Separate RGB texture defining the color of the surface in shadow (acts as translucency/subsurface map)

**Normal manipulation:** Transfer normals from a low-poly proxy to the high-poly model to get clean, 2D-like shadow shapes. Face normals are manually edited to avoid ugly shadow artifacts.

**Vertex painting:** R channel of vertex color acts as ambient occlusion adjustment. G and B channels control lit offset and line thickness.

**Outlines:** Inverted-hull method (duplicate mesh, flip normals, scale outward). NOT post-process.

**Key insight:** This workflow does NOT start from PBR textures. It's entirely hand-painted from scratch with NPR in mind. The "conversion" approach is fundamentally different from what these studios actually do.

### 2. Genshin Impact — miHoYo/HoYoverse

**Source:** Adrian Mendez shader breakdown (Unity URP implementation)

**Texture pipeline:**
- **Base color texture:** Hand-painted albedo (stylized, not PBR-derived)
- **Shadow color:** Defined as a tinted color multiplied over base, using `smoothstep(0, 0.1, NdotL)` for the light/shadow transition (soft threshold, not hard)
- **Face shadow texture:** Special 2-channel (R/G) texture hand-painted to define shadow shapes on the face at different light angles. R channel for 0-180°, G channel for 180-360°. This replaces NdotL for faces entirely.
- **Metallic regions:** Use a gradient texture sampled with `dot(Normal, ViewDir + LightDir)` — matcap-like approach, not PBR metallic/roughness
- **Anisotropic hair:** Fresnel-based with mask texture channel for highlight placement

**Post-processing (not bakeable):**
- Outline via Sobel filter on depth + normals (screen-space)
- Edge highlight (white rim) via Sobel on depth scene texture (NOT fresnel)
- Custom tonemapper (Gran Turismo) to preserve saturation

**Key insight:** Genshin doesn't use PBR textures at all. The entire pipeline is custom-authored for cel shading. The shadow transition is the critical differentiator — `smoothstep(0, 0.1, NdotL)` gives a slightly soft edge, not razor-sharp.

### 3. Blender NPR Project (Official, in development)

**Source:** Blender Developers Blog, May 2025

**Status:** Active development, post-Blender 5.0 release (Nov 2025+)

**Architecture:**
- **Multi-stage compositing** — object/material-level compositor that runs AFTER shading but BEFORE anti-aliasing. Each object defines its own appearance pipeline.
- **Converged input** — compositor runs on denoised/converged renders, solving the noisy-input problem that breaks sharp NPR effects (like color ramps on AO)
- **Anti-aliased output** — compositor runs per AA sample, then filters

**Current workaround (Blender today):** ShaderToRGB node in EEVEE (limited), or cumbersome scene-wide compositing

**Planned engine features:**
- Ray Queries
- Portal BSDF
- Custom Shading
- Depth Offset

**Key insight:** Blender's current NPR story is limited. ShaderToRGB only works in EEVEE. The new multi-stage compositor will allow per-object stylization — critical for mixed-style scenes.

### 4. Baking Stylized Shaders (EEVEE → Cycles → Export)

**Source:** RJean Lee, Medium (Apr 2025)

**Workflow for web/game engine export:**
1. Create stylized material in EEVEE (using Cycles-compatible nodes only)
2. UV unwrap the model
3. Switch to Cycles renderer
4. Create a new Image Texture node (unconnected but selected)
5. Bake Type: Combined → Bake
6. Save baked texture
7. Export model + texture as .glb

**Limitations:**
- Screen-space effects (outlines, bloom) CANNOT be baked
- EEVEE-only nodes (Specular BSDF, Shader to RGB) break in Cycles baking
- Lighting differences between EEVEE and Cycles mean slight visual mismatch
- Only works for effects that exist in the shader output itself

**Key insight:** You CAN bake NPR materials from Blender, but only the surface shading portion. Post-process effects must be recreated in the target engine.

### 5. Blender Community Techniques (StackExchange)

**Source:** Multiple Blender StackExchange answers

**Technique 1 — Shadow multiplication:**
- Capture shadows from a Diffuse BSDF clamped with a ColorRamp
- Multiply those shadow values over the original base color texture
- "Multiply it twice to really drive home the shadow effect"
- Use MixRGB node set to Multiply

**Technique 2 — Bake Toon BSDF to flat texture:**
- Add Image Texture node (unconnected), create new image
- Set up Toon BSDF or custom ColorRamp-based shader
- Bake to the image texture
- Result: flat toon-shaded texture with lighting baked in (view-dependent — only valid for fixed camera)

**Technique 3 — Posterization in shader:**
- `floor(color * steps) / steps` — quantizes color to N discrete levels
- Apply BEFORE lighting for color palette reduction
- Apply AFTER lighting for cel-shading bands

### 6. Malt Pipeline (Blender ↔ Godot shared rendering)

**Source:** Panthavma (PhD researcher in real-time NPR)

**Key innovation:** Same rendering code in both Blender and Godot via Malt custom pipeline. Two-pass approach:
- Pass 1: Render surface data (NdotL, position, normals) into buffers
- Pass 2: Screen-space shader reads buffers, applies toon quantization (step functions)

**Godot integration:** Uses Oddlib pipeline framework. The screen-space pass uses `canvas_item` shader sampling the first pass buffer.

**Key insight:** For Godot specifically, the recommended approach is NOT texture rebaking but rather a custom render pipeline that applies toon effects in real-time. This preserves dynamic lighting.

### 7. Redshift Toon Material (Maxon)

**Source:** Maxon Redshift documentation

**Key quote:** "Tone mapping is the most important element in defining the look of a Toon shader. It is the most powerful differentiator between NPR and PBR as it allows an artist direct control over lighting and shading."

**Implication:** The PBR→toon conversion is primarily about replacing the TONE MAPPING (how light values map to color bands), not the textures themselves. PBR albedo textures can often be used directly — it's the lighting model that changes.

---

## Practical Techniques for PBR → Toon Conversion

### Strategy A: Keep PBR albedo, replace lighting model (Recommended for Godot)

1. Use the PBR albedo texture as-is for base color
2. Discard metallic/roughness/normal maps (or use normal only for NdotL)
3. Replace PBR lighting with stepped NdotL: `smoothstep(0, edge_softness, dot(N, L))`
4. Define shadow color as tinted version of base color (lerp between shadow_tint and albedo)
5. Add specular as a sharp highlight: `step(threshold, dot(H, N))`

### Strategy B: Rebake into flat toon texture (for static/baked lighting)

1. Set up toon shader in Blender (ColorRamp on Diffuse BSDF)
2. Apply PBR albedo as base color input
3. Position fixed lighting for the "canonical" look
4. Bake Combined pass to new texture
5. Use with MeshBasicMaterial (unlit) in target engine
6. **Warning:** Baked lighting is view-dependent and non-dynamic

### Strategy C: Hand-paint control maps (AAA approach)

1. Start from PBR albedo, simplify/repaint to reduce detail and flatten colors
2. Create SSS/shadow color map (what color in shadow — usually warmer/more saturated)
3. Create ILM map with packed channels:
   - R: specular mask
   - G: shadow bias (paint darker where you want permanent shadow)
   - B: specular size
4. Edit normals for clean shadow shapes (transfer from simplified proxy mesh)
5. Paint inner lines into alpha or separate texture

### Strategy D: Posterization (quick stylization)

1. Keep PBR albedo
2. In shader: `color = floor(albedo * levels + 0.5) / levels` (reduces color palette)
3. Combine with stepped lighting for full cel look
4. Optionally bake the posterized result for export

---

## Tools & Addons Mentioned

| Tool | Purpose | URL |
|------|---------|-----|
| **Malt** | Custom render pipeline for Blender + Godot (same shaders both) | https://github.com/BlenderNPR/Malt |
| **Oddlib** | Godot-side render pipeline companion to Malt | https://github.com/panthavma/oddlib |
| **Deep Paint** | Blender addon for painterly NPR texturing | https://gakutada.gumroad.com/l/DeepPaint |
| **Stylized BSDF** | Complete NPR shader for Blender 5.1 | https://pojoquiet.gumroad.com/l/gwhvnb |
| **GGXrdShading** | Demo of Guilty Gear shading techniques | https://github.com/galloscript/GGXrdShading |
| **PGMGuiltyShader** | Unity implementation of Arc System Works technique | https://github.com/pakillottk/Unity3D-PGMGuiltyShader |
| **NonToon (lilxyzw)** | Shader combining PBR and NPR methods | https://github.com/lilxyzw/NonToon |
| **Node Wrangler** | Blender addon for fast PBR texture import (Ctrl+Shift+T) | Built into Blender |

---

## Key Takeaways for a Godot Toon Pipeline

1. **Don't rebake unless you need static/baked lighting.** Godot's shader system supports custom lighting — use Strategy A for dynamic toon shading.
2. **PBR albedo is often usable as-is** — the toon look comes from the lighting model, not the base color texture (unless you want extreme stylization).
3. **For maximum control, hand-paint shadow/ILM maps** alongside the albedo (Strategy C). This is what every AAA toon game does.
4. **Posterization is the simplest conversion** but produces generic results. Good for prototyping, not for a distinctive style.
5. **Normal editing is critical** — smooth normals from a simplified proxy mesh give clean shadow boundaries. This is a geometry step, not a texture step.
6. **Face shadows need special treatment** — NdotL looks terrible on faces. Use a directional shadow texture (Genshin approach) or heavily edited face normals.

---

## Sources

- GDC Vault: "GuiltyGearXrd's Art Style: The X Factor Between 2D and 3D" — https://gdcvault.com/play/1022031/GuiltyGearXrd-s-Art-Style-The
- Arc System Works GDC 2015 announcement — https://www.arcsystemworks.com/guilty-gear-xrds-art-style-the-x-factor-between-2d-and-3d-talk-from-gdc-2015-is-now-available-online/
- Guilty Gear Xrd Cel-Shading Techniques (Scribd summary) — https://fr.scribd.com/document/331351299/Blender-NPR-Cel-Shading-GuilltyGearXrd-Shader
- Unity3D-PGMGuiltyShader (ILM/SSS map implementation) — https://github.com/pakillottk/Unity3D-PGMGuiltyShader
- Genshin Impact Character Shader Breakdown (Adrian Mendez via juejin.cn) — https://juejin.cn/post/7206577654933569596
- Blender NPR Project blog post — https://code.blender.org/2025/05/npr-project/
- Malt + Godot pipeline (Panthavma) — https://panthavma.com/articles/godot-malt-pipeline-intro
- Baking stylized EEVEE to Three.js (RJean Lee) — https://yunchen-lee.medium.com/stylized-3d-model-for-the-web-blender-eevee-to-three-js-via-texture-baking-93e7200cda00
- Blender SE: Apply Toon Shader into texture — https://blender.stackexchange.com/questions/271156/how-to-apply-toon-shader-into-texture-material
- Blender SE: Posterize in shader — https://blender.stackexchange.com/questions/304301/posterize-node-in-material-shader
- Redshift Toon Material docs — https://help.maxon.net/r3d/blender/en-us/Content/html/Material+Toon.html
- 3D Game Shaders for Beginners: Posterization — https://lettier.github.io/3d-game-shaders-for-beginners/posterization.html
- Blender Studio: Blender + Godot workflow — https://studio.blender.org/blog/our-workflow-with-blender-and-godot/

---

## Open Questions

1. **What does Genshin's actual texture authoring pipeline look like internally?** The shader breakdown shows what textures exist, but not how artists create them (hand-paint from scratch vs. any automated steps from references).
2. **Can Substance Painter export toon-ready channel-packed maps (ILM format)?** Substance has smart materials — could a custom export template pack channels for NPR workflows?
3. **What's the performance cost of multi-pass toon rendering vs. baked textures in Godot 4.x?** Malt demonstrates the approach but Godot's native shader system has different constraints.
4. **How do modern AI style transfer tools (e.g., Reelmind, Blender NPR branch) compare to manual texture painting for production quality?**
