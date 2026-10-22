# Visual Problems: PBR Textures + Toon/Cel Shaders

## Summary

When photorealistic PBR textures are applied to toon/cel shaders, multiple visual artifacts emerge because PBR textures are designed for smooth, physically-accurate light response — while toon shaders deliberately quantize light into hard bands. The high-frequency detail that makes PBR textures look real becomes noise that shatters the flat, clean aesthetic toon shading depends on.

## Specific Visual Artifacts

### 1. Noisy Normal Maps → Shadow Speckle/Chattering

**What it looks like:** The clean shadow bands expected in toon shading become speckled, jittery, or appear as random salt-and-pepper noise instead of smooth shapes.

**Why it happens:** PBR normal maps encode micro-surface detail (pores, grain, bumps). When a toon shader quantizes the dot(N,L) calculation into 2-3 bands with a hard step function, each tiny normal variation can push individual pixels across the light/dark threshold. Instead of a clean shadow boundary, you get thousands of pixels flickering between bands.

**Reported by:** Hyper3D documentation: "Noisy normals shatter clean tone bands into speckle. Micro-detail belongs in realistic assets — for cel work, smooth surfaces and let the silhouette talk." Also extensively documented in aVersion of Reality's custom normals research.

**Technical detail:** The quantization function (e.g., `step(0.5, NdotL)`) amplifies normal map noise. In PBR, a normal variation of ±5° produces a subtle lighting gradient. In toon shading, that same ±5° variation at the shadow threshold creates binary light/dark spatter.

### 2. High-Frequency Albedo Detail → Visual Noise/Style Mismatch

**What it looks like:** The model looks "too busy" — neither realistic nor stylized. Fine texture details (wood grain, fabric weave, stone pores) become distracting noise that competes with the silhouette and form.

**Why it happens:** PBR albedo maps contain high spatial frequency detail to sell realism under smooth lighting. Toon shaders use flat color areas and rely on large shapes to communicate form. The micro-detail creates a "noise frequency that is too high" (Velan Studios) that distracts from key shapes.

**Reported by:** Erik McKenney at Velan Studios (2019): "Be they hand-painted textures, high-poly sculpted height maps, or fully-procedural materials, too many small details detract from the stylized look. They create a noise frequency that is too high, and they distract from the key shapes of the model." Also noted: "my work read as neither stylized nor realistic. It just looked broken."

**Solution:** Use broader, flatter color fields. Keep detail in medium-to-large frequency bands. Let silhouette carry the form rather than texture detail.

### 3. Roughness Map Interactions → Broken Specular Highlights

**What it looks like:** Specular highlights appear as harsh, scattered bright spots ("wet/oily" look) or get blown out beyond the expected toon style.

**Why it happens:** PBR roughness maps encode realistic variation across a surface (worn edges smoother, recesses rougher). When a toon shader tries to quantize specular response, the per-pixel roughness variation creates scattered, inconsistent highlight shapes instead of the clean single-lobe highlights expected in cartoon aesthetics. Values "too accurate tend to look too realistic" (McKenney).

**Reported by:** Funcom forums (UE5): "Skin and leather shaders are reacting to this light with extremely hard, sharp highlights. It looks as if the Roughness maps are being ignored or the Specular level is set to a non-organic value, resulting in a 'wet' or 'oily' appearance." McKenney at Velan Studios: "For a lot of my materials, the roughness value is much higher than its real-world counterpart. Less reflection allows for more color and a hint of brush strokes to come through."

**Solution:** Increase roughness significantly beyond physically-accurate values. Use uniform or very gently varying roughness rather than detailed roughness maps.

### 4. TAA Flickering with Hard Edges

**What it looks like:** The hard shadow/light boundaries in toon shading flicker rapidly between frames, creating a "buzzing" or "shimmering" effect especially on shadow edges.

**Why it happens:** Temporal Anti-Aliasing (TAA) works by blending sub-pixel jittered samples across multiple frames. Toon shader edges are mathematically discontinuous (step functions). The jittered samples land on different sides of the threshold each frame, and TAA's temporal blending cannot converge on a stable result — it continuously oscillates.

**Reported by:** Unreal Engine forums: "Toon shaders tend to flicker and cause strange and unwanted banding unless you also set the blend location to Before Tonemapping." Multiple developers report having to disable TAA entirely. GitHub toon-rp wiki documents custom temporal solutions with higher modulation factors to reduce toon-specific flickering.

**Solutions:**
- Disable TAA entirely (introduces jaggies)
- Set material blend location to Before Tonemapping (Unreal)
- Use MSAA instead (geometry-based, handles hard edges better)
- Custom temporal filtering with higher weight to current frame
- Soften the step function slightly (sigmoid instead of hard step)

### 5. Ambient Occlusion Noise in Flat Bands

**What it looks like:** Speckly, grainy dark patches appear in shadow bands, especially in concavities. The flat toon shadow regions look "dirty" instead of clean.

**Why it happens:** Screen-space ambient occlusion (SSAO) adds subtle darkening in creases and corners. In PBR rendering, this blends smoothly into the soft lighting. In toon shading, the AO values get quantized alongside the lighting, creating visible noise patterns in what should be uniform flat-shaded areas.

**Reported by:** RobertoCosta_Dev on UE forums: "I've nailed it down to static ambient occlusion that was being the most egregious contributor to the issue. Having the shadow threshold at 0.5 also contributed, pushing it down to 0.45 helped a lot." The developer spent 3 months fighting this issue.

**Solution:** Disable SSAO/DFAO, or apply AO as a multiply on top AFTER the toon quantization step rather than before.

### 6. Shadow Edge Instability from Mesh Topology

**What it looks like:** Shadow boundaries on toon-shaded models appear jagged, wavy, or lumpy — following the mesh's edge loops instead of forming clean artistic shapes.

**Why it happens:** Toon shading with hard shadow edges is "extremely sensitive to issues caused by mesh topology and vertex normal interpolation" (aVersion of Reality). Even slightly uneven loop spacing causes visible wobbles in the shadow boundary. In PBR with soft gradients, these imperfections are invisible. With toon's hard cutoff, every interpolation irregularity becomes a visible step.

**Reported by:** aVersion of Reality (2022): "Even just [slightly uneven loop spacing] is enough to screw up toon shading due to Linear Interpolation of Vertex Normals." Also: "Smoothing the model more destroys the shape before it fixes the shading, and cannot solve problems caused by topology and interpolation."

**Solutions:**
- Custom vertex normals (transferred from simplified proxy meshes)
- Geometry Nodes-based normal combination (Blender)
- Simplified proxy shapes for shadow calculation
- Higher subdivision specifically for smooth normal interpolation

### 7. Lumen/GI Noise in Quantized Bands

**What it looks like:** When using global illumination (Lumen, ray-traced GI), the inherent noise in GI calculations becomes visible as speckle within toon bands.

**Why it happens:** GI techniques like Lumen use stochastic sampling, producing slight per-pixel variation that gets smoothed by denoising in PBR. When this slightly-noisy lighting data hits a toon shader's step function, pixels near the threshold oscillate randomly between bands.

**Reported by:** Unreal forums: "When i played with lighting setting in the post process value i found that the noise disappears when lumen is removed."

**Solution:** Remove Lumen/stochastic GI, use simpler direct lighting, or add pre-quantization smoothing/blur to the light calculation.

### 8. Rim Light Artifacts on Flat Surfaces

**What it looks like:** Square or blocky artifacts appear at the edges of light influence areas, especially with rim/fresnel effects on large flat surfaces.

**Why it happens:** Rim lighting calculated in the `light()` function applies per-light with attenuation boundaries. When quantized, the attenuation falloff creates visible rectangular regions matching the light's influence volume. In PBR, attenuation fades smoothly to zero; in toon, it creates abrupt visible boundaries.

**Reported by:** Godot forums: "Note that rim behaves really badly on large flat surfaces." The issue was specifically about square artifacting on light fringes with a toon shader in Godot 4.3.

**Solution:** Calculate rim lighting separately from per-light calculations (use view direction only, not per-light attenuation). Apply only to directional lights.

## Root Cause Pattern

All these problems share a common root: **quantization amplifies noise.**

PBR rendering is designed to handle continuous, noisy input data gracefully — smooth gradients, subtle variations, stochastic sampling — because it produces smooth continuous output. Toon/cel shading applies discontinuous functions (step, threshold, posterize) that turn subtle variations into binary on/off decisions. Any input noise that was invisible in PBR becomes catastrophically visible when quantized.

The formula: `PBR_texture_detail × toon_quantization = amplified_visual_noise`

## What Practitioners Recommend

### Texture Preparation
1. **Flatten albedo** — reduce to a few large color fields, remove micro-detail
2. **Smooth or remove normal maps** — use only for large-form shapes, never micro-surface detail
3. **Increase and flatten roughness** — use uniform high roughness, remove roughness map detail
4. **Remove metallic variation** — binary metallic (0 or 1) works; avoid subtle metallic maps

### Shader Techniques
1. **Pre-filter lighting before quantization** — smooth the NdotL signal before applying step()
2. **Apply AO/GI post-quantization** — multiply screen effects after the toon bands, not before
3. **Soften thresholds slightly** — use smoothstep instead of step to reduce flicker sensitivity
4. **Disable TAA, use MSAA** — or implement custom temporal that respects hard edges
5. **Reduce shadow threshold from 0.5 to ~0.45** — gives tolerance for noise near the boundary

### Art Direction
1. **Exaggerate proportions** — larger shapes read better with flat shading (McKenney)
2. **Custom normals from simplified proxy meshes** — decouple shading shape from render mesh
3. **Let silhouette do the work** — toon relies on outline and form, not texture detail
4. **Design textures FOR the shader** — hand-painted flat textures outperform photoscanned PBR

## The Core Lesson for Learners

> **PBR textures are designed for gradients. Toon shaders are designed for flat bands. These goals are fundamentally opposed.** The more "realistic" your texture data, the worse it looks when quantized. Success requires either:
> - Preprocessing textures to remove high-frequency detail, OR
> - Writing shaders that selectively filter texture data before quantization

This is not a bug — it's a fundamental incompatibility between art approaches that requires intentional bridging.

## Sources

- McKenney, E. (2019). "Creating Stylized Art in a PBR World." Velan Studios / Medium.
  https://medium.com/velan-studios/tip-of-the-brush-creating-stylized-art-in-a-pbr-world-b803b91c082f
- aVersion of Reality (2022). "A Custom Normals Workflow for Clean, Stylized Toon Shading."
  http://www.aversionofreality.com/blog/2022/4/21/custom-normals-workflow
- Hyper3D (2024). "AI Cel-Shaded 3D Model Generator — Toon-Ready Assets."
  https://hyper3d.ai/styles/cel-shaded
- Unreal Engine Forums (2021). "Cel Shading Help: I'm at the end of my wits."
  https://forums.unrealengine.com/t/cel-shading-help-im-at-the-end-of-my-wits/230445
- Unreal Engine Forums (2022). "How to stop temporal anti aliasing for a toon shader."
  https://forums.unrealengine.com/t/how-to-stop-temporal-anti-aliasing-for-a-toon-shader/692479
- Godot Forum (2025). "Strange square artifacting on light fringes with a toon shader."
  https://forum.godotengine.org/t/strange-square-artifacting-on-light-fringes-with-a-toon-shader/99489
- Delt06/toon-rp Wiki (2023). "Anti-Aliasing" for toon rendering pipeline.
  https://github.com/Delt06/toon-rp/wiki/Anti%E2%80%90Aliasing
- Unity Discussions (2011). "Toon Shader vs toon/hand drawn texture?"
  https://discussions.unity.com/t/toon-shader-vs-toon-hand-drawn-texture/447305
- Unreal Engine Forums (2022). "Noise in Cel Shade Post process effect with Lumen."
  https://forums.unrealengine.com/t/noise-in-cel-shade-post-process-effect-with-lumen/639280
- Funcom Forums (2025). "UE5 Lumen & PBR Calibration Issues (Character Oiliness)."
  https://forums.funcom.com/t/technical-analysis-ue5-lumen-pbr-calibration-issues-character-oiliness-global-illumination-overflow/297686

## Open Questions

- What's the optimal pre-filter kernel size for NdotL before quantization? (Varies by band count and style)
- Do modern denoisers (DLSS, FSR) help or hurt toon shader stability compared to TAA?
- Are there established pipelines for automatically "flattening" PBR textures for toon use (beyond manual repaint)?
- How does Genshin Impact handle its toon shading with relatively detailed textures? (Custom ramp textures + carefully authored maps are the likely answer, but technical details are proprietary)
