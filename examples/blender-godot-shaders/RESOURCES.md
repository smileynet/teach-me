# Resources: Blender → Godot Shader Pipeline (Esoteric Ebb Style)

## Esoteric Ebb Art Style

| Source | What it covers | Trust |
|--------|---------------|-------|
| [Aftermath: "The Art Of Esoteric Ebb"](https://aftermath.site/esoteric-ebb-concept-art-illustrations/) | Visual breakdown, concept art, environment technique | ★★★ (press interview with developer) |
| [80.lv: Hand-Painted Backgrounds for D&D-Inspired RPG](https://80.lv/articles/check-out-these-beautiful-hand-painted-backgrounds-for-d-d-inspired-rpg) | Camera-aligned UV projection technique, texture sizes, 3D blockout → paint workflow | ★★★ (developer-sourced technical article) |
| [Final Weapon: Interview with Christoffer Bodegård](https://finalweapon.net/2026/03/17/interview-christoffer-bodegard-esoteric-ebb/) | Art pipeline evolution, design philosophy, influences | ★★★ (first-party interview) |
| [RPGWatch: "The Art of Ebb" devlog](https://rpgwatch.com/news/esoteric-ebb--the-art-of-ebb-57305.html) | Development process, art style iteration history | ★★ (press coverage of devlog) |
| [Official site](https://esotericebb.com/) | Reference screenshots, visual identity | ★★★ |

**Key technique:** 3D blockout → UV project from fixed camera → hand-paint large (4K–16K) textures overlaid on geometry. Limited palette, understated beauty, no flashy effects. Influenced by Disco Elysium, pre-rendered CRPG backgrounds (Baldur's Gate), Moebius/Tintin illustration.

## Blender NPR/Stylized Shaders

| Source | What it covers | Trust |
|--------|---------------|-------|
| [Maxime Garcia — NPR Shader in Blender](https://typhomnt.github.io/post/blender_npr/) | Full NPR breakdown: Diffuse, Specular, AO, SSS, Rim, Outline | ★★★ (detailed technical walkthrough) |
| [aVersion of Reality — Stylized Tree Shader](http://www.aversionofreality.com/blog/2022/8/7/stylized-tree-shader) | Radial normals, color mixing, surface gradients for foliage | ★★★ (artist technical blog) |
| [Blender Studio — Brushstroke Tools](https://studio.blender.org/tools/addons/brushstroke_tools) | Procedural 3D brushstroke rendering (film pipeline) | ★★★ (official Blender Studio) |
| [Trung Duy Ng — Anime Foliage Pipeline](https://trungduyng.substack.com/p/tutorial-blender-anime-foliage-pipeline) | Cel-shaded foliage, no translucency approach | ★★ (community tutorial) |
| [Shahriyar Shahrabi — Geometry Nodes Stylized Scenes](https://shahriyarshahrabi.medium.com/blender-geometry-nodes-create-stylized-scenes-e336967c7f84) | Geo Nodes for trees, procedural materials | ★★ (technical article) |
| [TextureGen — Bake Textures for Unity](https://texturegen.com/how-to-bake-textures-in-blender-for-unity/) | Baking pipeline (applicable to any engine) | ★★ (tutorial) |

## Godot Shaders & Pipeline

| Source | What it covers | Trust |
|--------|---------------|-------|
| [Godot Docs — Introduction to Shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/introduction_to_shaders.html) | GDShader language fundamentals | ★★★ (official docs) |
| [Godot Docs — Spatial Shaders](https://docs.godotengine.org/en/4.4/tutorials/shaders/shader_reference/spatial_shaders.html) | 3D shader reference (vertex, fragment, light) | ★★★ (official docs) |
| [Godot Docs — Making Trees](https://docs.godotengine.org/en/4.4/tutorials/shaders/making_trees.html) | Vertex color wind, stylized tree workflow | ★★★ (official docs) |
| [Godot Shaders — Complete Cel Shader for Godot 4](https://godotshaders.com/shader/complete-cel-shader-for-godot-4/) | Toon shading + outlines + posterization | ★★ (community, well-regarded) |
| [Godot Docs — Volumetric Fog](https://docs.godotengine.org/en/4.4/tutorials/3d/volumetric_fog.html) | FogVolume nodes, custom fog shaders | ★★★ (official docs) |
| [Blender Manual — glTF 2.0 Export](https://docs.blender.org/manual/en/4.2/addons/import_export/scene_gltf2.html) | What transfers via glTF, Principled BSDF mapping | ★★★ (official docs) |
| [Blender Studio — Workflow with Blender and Godot](https://studio.blender.org/blog/our-workflow-with-blender-and-godot/) | Professional Blender→Godot pipeline | ★★★ (official Blender Studio) |
| [Godot Docs — Custom Post-Processing](https://docs.godotengine.org/en/stable/tutorials/shaders/custom_postprocessing.html) | Screen-space effects, color grading | ★★★ (official docs) |

## Technique References (Cross-Cutting)

| Source | What it covers | Trust |
|--------|---------------|-------|
| [Godot Forum — Wind Shader with Demo Project](https://forum.godotengine.org/t/wind-shader-i-made-for-my-game-with-demo-project-to-download/70049) | Vertex displacement wind, downloadable demo | ★★ (community, tested) |
| [atsaturn — Writing a Cel Shader in Godot 4](https://atsaturn.hashnode.dev/writing-a-cel-shader-in-godot-4) | Step-by-step toon shader tutorial | ★★ (community tutorial) |
| [Generalist Programmer — Godot 4 Shaders Tutorial](https://generalistprogrammer.com/tutorials/godot-4-shaders-tutorial) | Beginner-to-intermediate GDShader walkthrough | ★★ (tutorial site) |
