# Research: How Existing Tutorials Teach Texture Analysis & PBR-to-Stylized Workflows

## Summary

Existing game dev tutorials teach texture analysis through a consistent pattern: physics-first theory → per-channel isolation with visual comparisons → progressive complexity → hands-on painting exercises. The PBR-to-stylized bridge is less well-served — most tutorials cover either full PBR or full toon/stylized as separate tracks, with few explicitly teaching the translation between them.

---

## Pedagogical Patterns Observed

### 1. Channel Isolation (The "One Map at a Time" Pattern)

Nearly every PBR texture tutorial introduces maps individually, showing:
- The raw texture map image (flat 2D)
- The rendered result with ONLY that map applied
- A before/after comparison (with vs without)

**Visual aids used:**
- Side-by-side renders: base mesh → +albedo → +normal → +roughness → +metalness
- "Strip" layouts showing the same object with one channel toggled off
- Color swatches with value ranges (e.g., "roughness 0.0 = mirror, 1.0 = chalk")

**Sources:** Adobe PBR Guide, TextureX beginner guide, ShareTextures guide, Tripo3D guides, SunStrike Studios tutorial.

### 2. The "Energy Conservation / Physics First" Foundation

High-quality tutorials (Adobe/Allegorithmic PBR Guide, Marmoset articles) begin with WHY before WHAT:
- Light behavior: absorption, reflection, scattering
- Energy conservation principle (reflected + absorbed = received)
- Microfacet theory (surface roughness at microscopic level)
- Then derive the need for each channel FROM the physics

This is the "first principles" approach. Lower-quality tutorials skip physics and jump to "here's what each map does" (recipe-based).

**Adobe PBR Guide structure:**
1. Light and matter interaction (physics)
2. What PBR means for artists (mental model shift)
3. Per-channel deep dives with value ranges and reference charts
4. Workflow comparison (metal/rough vs spec/gloss)
5. Practical creation guidelines with DO/DON'T examples

### 3. The "Checkerboard Test" Pattern (UV/Texel Density)

Before teaching texture content, production tutorials teach texture SPACE:
- Apply a checkerboard pattern to verify uniform texel density
- Show stretched vs correct UVs side by side
- This precedes any artistic texture work

**Source:** SunStrike Studios, Substance Painter workflows, multiple Udemy courses.

### 4. The "Ramp Texture" Bridge (PBR → Stylized)

The key pedagogical bridge between PBR and toon/stylized is the **toon ramp texture**:
- Start with realistic n·l (dot product) lighting
- Show it produces smooth gradients
- Apply a step function → instant "toon" look
- Use a ramp texture to control how many bands, what colors
- Progressive: 2-tone → 3-tone → gradient within bands → colored ramps

**This is the strongest existing pattern for the PBR-to-stylized translation.**

**Key tutorials using this:**
- Roystan.net Unity Toon Shader Tutorial
- Panthavma's "Toon Shading Fundamentals"
- Redshift/Maxon Toon Material documentation
- Godot docs (render_mode diffuse_toon, specular_toon)

### 5. Step-by-Step Build-Up (Additive Layering)

The Roystan toon shader tutorial exemplifies this pattern:
1. Start with flat color (unlit)
2. Add directional light (n·l calculation)
3. Apply step function (toon banding)
4. Add ambient light
5. Add specular reflection (Blinn-Phong)
6. Apply toon threshold to specular
7. Add rim lighting
8. Add shadows

Each step has a visual screenshot showing the result. The reader sees the image change with each addition. ~40 minutes estimated completion time.

### 6. Value Range Reference Charts

The Allegorithmic/Adobe PBR Guide popularized reference charts showing:
- Measured albedo values for real materials (charcoal=0.04, snow=0.81)
- Roughness bands (polished metal=0.1-0.2, rough wood=0.5-0.7)
- Binary metalness guidelines

These are used as "cheat sheets" that learners bookmark and return to.

### 7. "What NOT to Do" Anti-Pattern Galleries

Production-oriented tutorials (SunStrike, Marmoset) include common mistakes:
- Baked AO in albedo → "muddy under dynamic lighting"
- Glossy everything → "plastic sheen"
- UV stretching → "smeared paint at distance"
- Inconsistent palette across artists

Visual format: bad example alongside corrected version.

---

## Visual Aids Taxonomy

| Aid Type | Where Used | Teaching Purpose |
|----------|-----------|-----------------|
| Side-by-side renders (with/without channel) | Adobe PBR Guide, all beginner guides | Isolate each channel's contribution |
| Sphere under controlled lighting | Roystan, Panthavma, every shader tutorial | Neutral geometry to show lighting math |
| Ramp texture strips (1D gradient images) | Panthavma, Redshift docs, Godot community | Show how color maps to lighting coefficient |
| Value range charts (measured materials) | Adobe PBR Guide, ShareTextures | Provide calibrated starting points |
| Checkerboard UV overlays | SunStrike, Substance Painter courses | Verify texel density |
| Wireframe + textured turntables | SunStrike, ArtStation tutorials | Show relationship between mesh and texture |
| Before/after comparison (PBR → stylized) | Rare — gap in existing tutorials | Demonstrate what changes in the translation |
| Annotated shader code with arrows to visual | Roystan, Panthavma | Connect math to visual output |
| Node graph screenshots | Unity Shader Graph, Blender tutorials | Show data flow between maps |
| Material dictionary swatches | SunStrike (production guides) | Establish shared visual language for teams |

---

## Exercises Given to Learners

### Beginner Exercises
1. **Texture painting a simple prop** (CG Cookie): unwrap a provided model (axe, sword), paint albedo by hand following a style guide. Emphasis on clean color without baked lighting.
2. **Checkerboard test exercise**: apply a checker pattern, identify and fix UV stretching.
3. **Value matching**: given a photo reference, identify and match roughness/albedo values using a color picker and reference chart.

### Intermediate Exercises
4. **Channel isolation drill**: given a full PBR material, view each channel in isolation and describe what information each carries.
5. **Smart material breakdown**: take a pre-made Substance Painter smart material, examine each layer's mask and generator, explain how edge wear is driven.
6. **Convert a PBR material to stylized**: (rarely taught explicitly — identified as a gap)

### Toon Shader Exercises
7. **Create a custom ramp texture**: paint a 256×1 pixel gradient and apply it as a toon ramp to a sphere. Observe how changing colors affects the mood.
8. **Modify threshold parameters**: adjust smoothstep bounds in a toon shader to control edge softness.
9. **Compare render modes**: toggle between PBR and toon render modes on the same mesh, identify what changes.

---

## How Toon Shaders Handle Textures (Simplified vs Full PBR)

### What toon shaders typically USE from PBR textures:
- **Albedo/Base Color**: Always used. Sometimes split into "lit color" and "shadow color" textures.
- **Normal Map**: Often used for surface detail but discretized by the step function.
- **Roughness**: Sometimes ignored entirely (toon specular uses its own threshold). Sometimes used to control specular highlight size.
- **Metalness**: Usually ignored in toon pipelines (reflection model is non-physical).
- **AO**: Sometimes used as a multiply, sometimes baked into the shadow color.

### What toon shaders ADD beyond PBR:
- **Ramp textures** (1D or 2D): map lighting coefficient → color
- **Outline parameters**: edge detection thickness, color
- **Shadow color overrides**: explicit lit/shadow color pairs rather than PBR-computed shading
- **Halftone/pattern textures**: screen-space patterns for manga/comic styles

### The Translation Pattern:
```
PBR (continuous) → Toon (discrete)
  Smooth lighting gradient → Step function with N bands
  Fresnel-based rim → Threshold-based rim
  Microfacet specular → Hard-cut specular dot
  AO from maps → Baked or ignored
  Normal affects gradient → Normal affects band boundaries
```

---

## Gap Analysis: What's NOT Well Taught

1. **The explicit PBR-to-stylized translation** — tutorials teach EITHER PBR OR toon, rarely the conversion workflow. A learner who has PBR textures and wants to use them in a toon pipeline gets almost no guidance.

2. **Texture analysis for shader authors** — knowing which channels are "load-bearing" for a particular visual style. If your shader ignores roughness, you don't need roughness maps — but no tutorial frames it this way.

3. **What makes a texture "toon-friendly"** — e.g., clean flat albedo colors work better than photographic detail; normal maps can be simplified or flattened; roughness is often irrelevant or dramatically simplified.

4. **Visual comparison of the same scene with increasing stylization** — starting realistic and progressively simplifying. The inverse of the "build up PBR channel by channel" pattern.

5. **Decision framework for which PBR channels to keep vs discard** based on art direction goals.

---

## Pedagogical Recommendations for Our Lessons

Based on this research, the most effective approach for teaching texture analysis in a shader-focused curriculum:

1. **Start with "what does each channel DO to the final pixel?"** — channel isolation with visual comparison (proven pattern).

2. **Use a real PBR texture set on a real mesh** (not a sphere) to ground the analysis in recognizable materials.

3. **Progressive removal exercise**: start with all PBR channels, remove one at a time, observe what degrades. This teaches which channels are critical vs optional for a given style.

4. **Introduce the ramp as the bridge mechanism** — show how a continuous PBR lighting result becomes discrete toon banding.

5. **Create a decision table**: "If your art direction requires X look, you need Y channels" — this fills the identified gap.

6. **Use the "same mesh, two pipelines" comparison** — render one asset PBR-realistic and toon-stylized side by side, annotate what changed in the shader inputs.

---

## Source URLs

### PBR Fundamentals & Texture Guides
- Adobe PBR Guide Part 1: https://www.adobe.com/learn/substance-3d-designer/web/the-pbr-guide-part-1
- Adobe PBR Guide Part 2: https://www.adobe.com/learn/substance-3d-designer/web/the-pbr-guide-part-2
- ShareTextures PBR Guide: https://www.sharetextures.com/blog/what-pbr-textures-are
- TextureX Beginner Guide: https://texturex.com/pbr-textures-guide-beginners-2026
- Tripo3D PBR Maps List: https://www.tripo3d.ai/blog/pbr-texture-maps-list
- Marmoset PBR Theory: https://marmoset.co/posts/basic-theory-of-physically-based-rendering/
- Marmoset Texture Conversion: https://marmoset.co/posts/pbr-texture-conversion/
- SunStrike Studios Texturing Guide: https://sunstrikestudios.com/en/texturing_3d_models_for_games

### Toon/Stylized Shader Tutorials
- Roystan Toon Shader (Unity): https://roystan.net/articles/toon-shader/
- Panthavma Toon Shading Fundamentals: http://panthavma.com/articles/shading/toonshading/
- Wayline.io Unity Toon Shader 2023: https://www.wayline.io/blog/unity-toon-shader-tutorial-2023
- Redshift Toon Material (Blender): https://help.maxon.net/r3d/blender/en-us/Content/html/Material+Toon.html
- Kodeco UE4 Cel Shading: https://www.kodeco.com/146-unreal-engine-4-cel-shading-tutorial
- Godot Toon Shader (community): https://godotshaders.com/shader/toon-shader/
- AtSaturn Godot Cel Shader writeup: https://atsaturn.hashnode.dev/writing-a-cel-shader-in-godot-4

### Stylized Texturing Workflows
- Ishmael "Creating Stylized Textures for Games" (Gumroad): https://app.gumroad.com/l/levelup_stylized
- Thiago Klafke Stylized Environment Texturing: https://thiagoklafke.gumroad.com/l/stylizedtexturing
- 80.lv Hand-Painted Workflow Study: https://80.lv/articles/studying-hand-painted-texturing-workflow-for-stylized-art
- Gnomon Workshop Stylized Environments: https://www.thegnomonworkshop.com/workshops/stylized-environment-creation-for-games

### Academic/Pedagogical
- Wolfe "Teaching Texture Mapping Visually" (1997): https://www.cse.iitb.ac.in/~cs475/fall2016/handouts/1997--wolfe--teaching_texture_mapping.pdf
- ResearchGate listing: https://www.researchgate.net/publication/228898185_Teaching_Texture_Mapping_Visually
- University of Milan 3D Video Games texture lectures: https://tarini.di.unimi.it/teaching/3DVG2026/10_textures_1.pdf
- Scratchapixel Introduction to Texturing: https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-texturing/introduction-to-texturing.html

### Godot-Specific
- Godot 4.x Shader Tutorial (Second 3D Shader): https://docs.godotengine.org/en/4.4/tutorials/shaders/your_first_shader/your_second_3d_shader.html
- CaptainProton FlexibleToonShader: https://github.com/CaptainProton42/FlexibleToonShaderGD
- FlatKit Stylized Surface: https://flatkit.dustyroom.com/stylized-surface/

### Exercises & Courses
- CG Cookie "Texture Painting an Ax": https://cgcookie.com/exercises/texture-painting-an-ax
- Udemy Hand-Painted Texturing: https://www.udemy.com/course/3dmotive-learn-the-hand-painted-texturing-style-for-video-games/
- Generalist Programmer Substance Painter: https://generalistprogrammer.com/tutorials/substance-painter-game-texturing-complete-pbr-workflow
- Generalist Programmer Blender Texture Painting: https://generalistprogrammer.com/tutorials/blender-texture-painting-complete-game-asset-tutorial
