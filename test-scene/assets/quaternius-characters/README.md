# Quaternius Character Models

CC0 character models from the **Ultimate Animated Character Pack** by [Quaternius](https://quaternius.com/).

## Source

- Pack: [Ultimate Animated Character Pack](https://www.patreon.com/posts/ultimate-pack-31403272)
- Google Drive: https://drive.google.com/drive/folders/1sNi1AfenfPRrvRt5yfaj5QMMd6KKcUJ5
- License: [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)

## Files

| File | Vertices | Materials | Why selected |
|------|----------|-----------|--------------|
| `Knight_Golden_Female.glb` | 9,264 | Skin, Armor, Armor_Dark, Detail, Red, Hair | Hard armor plates + smooth skin — ideal for outline edge detection |
| `Viking_Female.glb` | 10,270 | Skin, Light, Main, Pants, Hair, Face | Mixed cloth/leather + exposed skin — tests soft-to-hard transitions |
| `Wizard.glb` | 9,286 | Skin, Clothes, Belt, Gold, Hat, Hair, Face | Flowing robes (smooth) + belt/hat accessories (hard edges) |

## Properties

All models share:
- glTF 2.0, binary (GLB)
- Humanoid armature with 23 bones
- 17 animations each (Idle, Walk, Run, Jump, SwordSlash, Death, etc.)
- Low-poly stylized aesthetic (~9-10K vertices)
- Color materials only (no textures) — flat shading, perfect for toon/outline shaders

## Conversion

Original `.gltf` (with embedded data URIs) converted to `.glb` using `@gltf-transform/cli`:

```bash
npx @gltf-transform/cli copy input.gltf output.glb
```
