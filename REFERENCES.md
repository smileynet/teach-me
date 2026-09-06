# References

Reference repos cloned into `.references/` (gitignored). Rehydrate all with `mise run rehydrate`
— it greps the `git clone` lines below and clones any that are missing (existing dirs are skipped).

Grouped by the track that motivated the clone. `inkgd` is the one exception: it is **vendored**
into `ink-test-project/addons/inkgd/`, not cloned to `.references/` — but its source is kept
here for provenance (see the Ink toolchain note).

## Ink toolchain (ink-godot lesson track)

| Repo | What it shows |
|------|--------------|
| `ink` | inkle's reference ink compiler + language (inklecate). The authoritative ink spec + examples. |
| `ink-cheat-sheet` | Condensed ink syntax reference — quick lookup for knots/diverts/weave/variables. |
| `godot-ink` | paulloz's C# ink integration for Godot — cross-reference for the GDScript inkgd runtime. |
| `inkgd` | ephread's GDScript ink runtime. **Vendored** into `ink-test-project/addons/inkgd/` from branch `godot4` @ `fea9098` (2024-01-28) — no official Godot-4 release exists. Provenance + drift-check in `ink-test-project/addons/inkgd/VENDOR.md`; policy in ADR 0013. The `.references/inkgd` clone is for reading upstream, not the runtime source of truth. |

```
git clone --depth 1 https://github.com/inkle/ink.git .references/ink
git clone --depth 1 https://github.com/sawradip/ink-cheat-sheet .references/ink-cheat-sheet
git clone --depth 1 https://github.com/paulloz/godot-ink.git .references/godot-ink
git clone --depth 1 https://github.com/ephread/inkgd.git .references/inkgd
```

## gdshader tooling (shader validation exploration)

Explored for validating `.gdshader` lesson code (no CLI compiler exists — see
`code-validation-teaching.md`). These are the LSP / parser / toolkit landscape.

| Repo | What it shows |
|------|--------------|
| `tree-sitter-gdshader` | tree-sitter grammar for gdshader — parser-based syntax checking. |
| `godot-gdshader-toolkit` | gdshader tooling/utilities. |
| `gdshader-lsp` | GodOfAvacyn's gdshader language server (Rust). |
| `gdshader-language-server` | armsnyder's gdshader language server (Go) — alternative LSP implementation. |
| `gdshader-lsp-cpp` | Dead-Shrimp-Studio's C++ gdshader LSP — a third implementation for cross-reference. |

```
git clone --depth 1 https://github.com/GodOfAvacyn/tree-sitter-gdshader.git .references/tree-sitter-gdshader
git clone --depth 1 https://github.com/grayespinoza/godot-gdshader-toolkit.git .references/godot-gdshader-toolkit
git clone --depth 1 https://github.com/GodOfAvacyn/gdshader-lsp.git .references/gdshader-lsp
git clone --depth 1 https://github.com/armsnyder/gdshader-language-server.git .references/gdshader-language-server
git clone --depth 1 https://github.com/Dead-Shrimp-Studio/gdshader-lsp-cpp.git .references/gdshader-lsp-cpp
```

## Toon shading & texture prep (godot-gamedev / blender-texture-prep tracks)

| Repo | What it shows |
|------|--------------|
| `godot4-cel-shader` | eldskald's Godot 4 cel/toon shader — reference cel-shading implementation. |
| `posterize-to-palette` | Aurora_Bee's posterize→palette technique (Codeberg) — the color-simplification approach behind lessons 16–17. |

```
git clone --depth 1 https://github.com/eldskald/godot4-cel-shader .references/godot4-cel-shader
git clone --depth 1 https://codeberg.org/Aurora_Bee/posterize-to-palette .references/posterize-to-palette
```

## Outline / distance-field references (#216 shader-track exploration)

Clones for the outline + distance-field exploration (relates to `godot-toon-shaders`
`advanced-outlines` topic + the `jfa-distance-fields` expansion opportunity).

| Repo | What it shows |
|------|--------------|
| `godot-jfa-madalaski` | Jump Flood Algorithm outlines in Godot 4 via CompositorEffect (compute) — the JFA distance-field technique `advanced-outlines` references. |
| `godot-distance-field-outlines` | pink-arcana's JFA/SDF outline demo (Godot) — a second, documented JFA implementation for cross-reference. |
| `godot-outlines` | L0UARN's Godot outline shader — inverted-hull / screen-space outline reference. |
| `demo-pixel-outline-godot` | SimonPiCarter's pixel-outline demo — pixel-perfect edge outline approach. |
| `Acerola-Compute` | GarrettGunnell's Godot compute-shader helper/examples (Acerola) — compute-shader patterns, relevant to JFA/post-process. |
| `Gamelogic-Outlines` | Gamelogic's outline techniques — **Unity** project (reference for technique/approach, not Godot code). |

```
git clone --depth 1 https://github.com/Madalaski/godot-jfa-madalaski .references/godot-jfa-madalaski
git clone --depth 1 https://github.com/pink-arcana/godot-distance-field-outlines.git .references/godot-distance-field-outlines
git clone --depth 1 https://github.com/L0UARN/godot-outlines.git .references/godot-outlines
git clone --depth 1 https://github.com/SimonPiCarter/demo_pixel_outline_godot.git .references/demo-pixel-outline-godot
git clone --depth 1 https://github.com/GarrettGunnell/Acerola-Compute .references/Acerola-Compute
git clone --depth 1 https://github.com/Gamelogic-Code/Outlines .references/Gamelogic-Outlines
```


## Official docs — first-party spec sources (gltf-format / godot-* tracks)

Authoritative documentation cloned for the glTF-format, godot-asset-pipeline, godot-3d-animation,
and godot-3d-navigation tracks. These are the L4 first-party sources lessons cite — kept local so
authoring/validation reads from a pinned checkout rather than fetching (some Blender manual mirrors
403 to bots). Shallow clones; large (Blender manual carries images).

| Repo | What it shows |
|------|--------------|
| `blender-manual` | The official Blender user manual (RST/Sphinx source, projects.blender.org). Authoritative for the glTF exporter — `manual/addons/scene_gltf2.rst` — plus modeling/rigging/animation. NOTE: latest moved the glTF page to `manual/addons/`, not the old `addons/import_export/` URL path. |
| `godot-docs` | The official Godot Engine documentation (RST source). Authoritative for glTF import (`tutorials/assets_pipeline/importing_3d_scenes/`), the `GLTF*` class refs (`classes/class_gltf*.rst`), AnimationTree, and navigation. `latest` = current 4.x. |

```
git clone --depth 1 https://projects.blender.org/blender/blender-manual.git .references/blender-manual
git clone --depth 1 https://github.com/godotengine/godot-docs.git .references/godot-docs
```
