# Godot 4 Texture Import & Custom Shader PBR Textures

## Summary

Godot 4's shading language provides texture hints (`source_color`, `hint_normal`, `hint_default_white`, etc.) that control both inspector behavior and internal color space handling. When using custom spatial shaders (not StandardMaterial3D), you declare `uniform sampler2D` with appropriate hints, and Godot exposes them as texture slots in the ShaderMaterial inspector. Color space correctness depends on using `source_color` for sRGB data and `hint_normal` for normal maps — getting this wrong produces washed-out or broken lighting.

## 1. Assigning Textures to Shader Uniforms in the Inspector

When you declare a `uniform sampler2D` in a `.gdshader` file, Godot automatically exposes it in the ShaderMaterial's inspector panel. You assign textures by:

1. Select the MeshInstance3D → Material → ShaderMaterial
2. Click the ShaderMaterial to expand it
3. Each `uniform sampler2D` appears as a texture slot under "Shader Parameters"
4. Drag-and-drop or click to assign a Texture2D resource

**From GDScript:**
```gdscript
material.set_shader_parameter("albedo_texture", preload("res://textures/albedo.png"))
```

**Important:** The parameter name in `set_shader_parameter()` must match the uniform name exactly (case-sensitive). The inspector shows a capitalized/prettified version but the API uses the raw name.

**Default textures:** If a texture is not set in the ShaderMaterial, you can provide a default via `Shader.set_default_texture()`, or use hints like `hint_default_white` / `hint_default_black` to control the fallback.

## 2. Texture Hints in gdshader (Full Reference)

### Color/Data Hints

| Hint | Purpose | When to use |
|------|---------|-------------|
| `source_color` | Marks texture as sRGB → performs sRGB-to-linear conversion on sample | **Albedo/color textures** — any texture containing authored color data |
| `hint_normal` | Marks as normal map → triggers reimport as RGTC (RG channels only), Godot reconstructs blue in shader | **Normal maps** |
| `hint_default_white` | Default to opaque white (1,1,1,1) when no texture assigned | **Roughness, metallic, AO** — scalar data where "no texture" means full value |
| `hint_default_black` | Default to opaque black (0,0,0,1) when no texture assigned | **Emission, height** — where "no texture" means zero |
| `hint_default_transparent` | Default to transparent black (0,0,0,0) | Masks, alpha data |
| `hint_anisotropy` | Marks as anisotropy flowmap, default to right | Anisotropy direction maps |
| `hint_roughness_r` / `_g` / `_b` / `_a` / `_normal` / `_gray` | Roughness limiter on import (reduces specular aliasing) | Roughness textures in 3D |

### Filter/Repeat Hints

| Hint | Effect |
|------|--------|
| `filter_linear` | Linear filtering |
| `filter_nearest` | Nearest filtering (pixel art) |
| `filter_linear_mipmap` | Linear + mipmaps |
| `filter_linear_mipmap_anisotropic` | Linear + mipmaps + anisotropic |
| `repeat_enable` | Tiling enabled |
| `repeat_disable` | Tiling disabled |

### Combining Hints

Multiple hints are comma-separated:
```glsl
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D normal_map : hint_normal, filter_linear_mipmap, repeat_enable;
uniform sampler2D roughness_texture : hint_roughness_r, hint_default_white;
```

## 3. Color Space: sRGB vs Linear

### The Rule

Godot 4 (Forward+ and Mobile renderers) renders in **linear color space**. Textures containing color data are stored as sRGB on disk and must be converted to linear on sample.

| Texture type | Color space on disk | Hint needed | What happens without hint |
|-------------|--------------------|----|---|
| Albedo / diffuse color | sRGB | `source_color` | Colors appear washed out (too bright, low contrast) |
| Normal map | Linear | `hint_normal` | Wrong compression, possible blue channel waste |
| Roughness | Linear | None (no hint) | Correct as-is |
| Metallic | Linear | None | Correct as-is |
| AO | Linear | None | Correct as-is |
| Emission color | sRGB | `source_color` | Emission appears washed out |
| Height/displacement | Linear | None | Correct as-is |

### `source_color` is REQUIRED in Forward+ and Mobile

The docs state: "Using `source_color` hint is required in the Forward+ and Mobile renderers." Without it, sRGB textures are sampled as linear data → they look washed out.

For the **Compatibility** renderer, `source_color` is optional but recommended for portability.

## 4. Normal Map Import Settings

### What `hint_normal` Does

When you declare `uniform sampler2D normal_map : hint_normal;` and assign a texture:

1. **Triggers reimport** — Godot detects the texture is used as a normal map
2. **Sets Compress > Normal Map** to "Enabled" in the texture's import settings
3. **Uses RGTC compression** — Only red and green channels stored (RG format); blue is reconstructed in the shader as `sqrt(1.0 - r*r - g*g)`
4. **Saves VRAM** — RGTC preserves detail better than DXT5 for normal data at same memory cost

### Import Settings for Normal Maps

In the Import dock (select the texture file):
- **Compress > Normal Map**: `Detect` (default) → auto-detects when used with `hint_normal`; set to `Enabled` to force
- **Compress > Channel Pack**: `sRGB Friendly` prevents RG-only format; `Optimized` allows it
- **Process > Normal Map Invert Y**: Enable if your source uses DirectX-style (Y-) normals (e.g., from Substance, some Blender exports). Godot expects OpenGL-style (Y+).
- **Mipmaps > Generate**: **Enable for 3D** — normal maps need mipmaps to avoid shimmer at distance

### Poly Haven Normal Maps

Poly Haven provides OpenGL-format normal maps (Y+) — these work directly in Godot without inverting Y. No special handling needed beyond enabling mipmaps and letting `hint_normal` trigger RGTC compression.

## 5. Complete Example: PBR Custom Shader

```glsl
shader_type spatial;

// Color data → needs source_color for sRGB→linear conversion
uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_texture : source_color, hint_default_white, filter_linear_mipmap, repeat_enable;

// Scalar data → no color conversion needed
uniform float roughness : hint_range(0.0, 1.0) = 0.5;
uniform sampler2D roughness_texture : hint_roughness_r, hint_default_white, filter_linear_mipmap, repeat_enable;

uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D metallic_texture : hint_default_white, filter_linear_mipmap, repeat_enable;

// Normal map → hint_normal triggers RGTC reimport
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform sampler2D normal_texture : hint_normal, filter_linear_mipmap, repeat_enable;

// AO → linear data
uniform sampler2D ao_texture : hint_default_white, filter_linear_mipmap, repeat_enable;

void fragment() {
    vec4 albedo_sample = texture(albedo_texture, UV);
    ALBEDO = albedo_color.rgb * albedo_sample.rgb;
    
    ROUGHNESS = roughness * texture(roughness_texture, UV).r;
    METALLIC = metallic * texture(metallic_texture, UV).r;
    
    NORMAL_MAP = texture(normal_texture, UV).rgb;
    NORMAL_MAP_DEPTH = normal_strength;
    
    AO = texture(ao_texture, UV).r;
}
```

## 6. glTF Import and Texture Color Space

When importing glTF models:
- Godot's glTF importer automatically assigns correct color spaces to textures based on their material slot (albedo gets sRGB, normal/roughness/metallic get linear)
- Extracted materials use StandardMaterial3D by default — if you replace with a ShaderMaterial, you must re-declare the correct hints yourself
- **Gotcha**: If you extract textures from a glTF and reassign them to a custom shader without `source_color` on the albedo, colors will be wrong

## 7. Gotchas When Using Poly Haven Textures with Custom Shaders

1. **Always use `source_color`** on albedo/diffuse uniforms — Poly Haven textures are sRGB-encoded PNGs/EXRs for color maps
2. **Normal maps are OpenGL format** (Y+) — no need to invert Y in import settings
3. **Enable mipmaps** for all 3D textures (Import dock → Mipmaps > Generate = true). Poly Haven textures are high-res; without mipmaps they shimmer at distance
4. **Roughness/Metallic/AO are single-channel** — sample `.r` only. Use `hint_default_white` so missing textures default to "full roughness" / "full AO" rather than black
5. **Don't use `source_color` on non-color data** — roughness, metallic, AO, height, and normal maps are linear data. Adding `source_color` to these will make them too dark (double gamma correction)
6. **Displacement/height maps** need no special hint — they're linear scalar data
7. **VRAM compression mode**: For 3D textures, use "VRAM Compressed" (the default when Godot detects 3D usage) rather than "Lossless" to save GPU memory. Poly Haven 4K textures can consume enormous VRAM without compression.
8. **Texture import "Detect 3D"**: Godot auto-detects when a texture is first used in a 3D context and reimports with VRAM compression + mipmaps. If you import textures before assigning them to materials, they may initially import as 2D. Reassigning triggers a reimport prompt.

## 8. Setting Import Options Manually

For each texture file, select it in the FileSystem dock → Import tab:

| Texture role | Compress Mode | Normal Map | Mipmaps | Channel Pack |
|-------------|--------------|------------|---------|-------------|
| Albedo/Color | VRAM Compressed | Detect (disabled) | Generate: On | sRGB Friendly |
| Normal | VRAM Compressed | Enabled | Generate: On | Optimized (allows RG) |
| Roughness | VRAM Compressed | Detect (disabled) | Generate: On | Optimized |
| Metallic | VRAM Compressed | Detect (disabled) | Generate: On | Optimized |
| AO | VRAM Compressed | Detect (disabled) | Generate: On | Optimized |
| Height | VRAM Compressed | Detect (disabled) | Generate: On | Optimized |

After changing import settings, click "Reimport" (or it happens automatically).

## Sources

- [L2:verified] Godot Shading Language Reference (stable) — https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/shading_language.html
- [L4:verified] ResourceImporterTexture class (4.5) — https://docs.godotengine.org/en/4.5/classes/class_resourceimportertexture.html
- [L4:verified] VisualShaderNodeTextureParameter (4.7) — https://docs.godotengine.org/en/4.7/classes/class_visualshadernodetextureparameter.html
- [L6:reported] Godot Forum: "hint_normal triggers the reimport of a texture as a normal map" (Calinou) — https://forum.godotengine.org/t/what-exactly-does-hint-normal-in-shaders-do-what-do-other-hints-do/9793
- [L4:verified] ShaderMaterial class (4.3) — https://docs.godotengine.org/en/4.3/classes/class_shadermaterial.html
- [L6:reported] GodotShaders.com "Colored Glass" example (shows complete uniform declarations) — https://godotshaders.com/shader/godot-4-2-colored-glass/

## Open Questions

- The exact behavior of `hint_roughness_normal` (roughness limiter guided by normal map) is not well-documented for custom shaders — it's primarily an import-time optimization, but unclear if it affects sampling in custom shader contexts
- Whether `source_color` on sampler2D triggers any additional GPU-side conversion beyond the sRGB→linear decode on texture fetch (likely not — it's just a format flag)
