# References

Cloned repos in `.references/` for the Preact migration. Rehydrate with `mise run rehydrate`.

## Preact No-Build Patterns

| Repo | What it shows |
|------|--------------|
| `preact-buildless-starter` | Project structure, import maps, HTM components without bundler |
| `todomvc-htm-preact` | Complete app with HTM tagged templates, signals, component composition |
| `preact-nobuild-example` | Real project without bundler — routing, state, multiple pages |
| `preact-standalone-bundle` | Single-file bundle of Preact+HTM+Signals for fully offline use |

## Infrastructure

| Repo | What it shows |
|------|--------------|
| `es-module-shims` | Polyfill for import maps in older browsers (Firefox support) |
| `dagre-fork` | HassanMojab's dagre fork with `layer` property for rank constraints |

## Ink toolchain

| Repo | What it shows |
|------|--------------|
| `inkgd` | ephread's GDScript ink runtime. **Vendored** into `ink-test-project/addons/inkgd/` from branch `godot4` @ `fea9098` (2024-01-28) — no official Godot-4 release exists. Provenance + drift-check in `ink-test-project/addons/inkgd/VENDOR.md`; policy in ADR 0013. |

## Shader / outline references (#216 shader-track exploration)

Clones for the outline + distance-field exploration (relates to `godot-toon-shaders`
`advanced-outlines` topic + the `jfa-distance-fields` expansion opportunity).

| Repo | What it shows |
|------|--------------|
| `godot-jfa-madalaski` | Jump Flood Algorithm outlines in Godot 4 via CompositorEffect (compute) — the JFA distance-field technique `advanced-outlines` references. |
| `godot-distance-field-outlines` | pink-arcana's JFA/SDF outline demo (Godot) — a second, documented JFA implementation for cross-reference. |
| `Acerola-Compute` | GarrettGunnell's Godot compute-shader helper/examples (Acerola) — compute-shader patterns, relevant to JFA/post-process. |
| `Gamelogic-Outlines` | Gamelogic's outline techniques — **Unity** project (reference for technique/approach, not Godot code). |

```
git clone --depth 1 https://github.com/Madalaski/godot-jfa-madalaski .references/godot-jfa-madalaski
git clone --depth 1 https://github.com/pink-arcana/godot-distance-field-outlines .references/godot-distance-field-outlines
git clone --depth 1 https://github.com/GarrettGunnell/Acerola-Compute .references/Acerola-Compute
git clone --depth 1 https://github.com/Gamelogic-Code/Outlines .references/Gamelogic-Outlines
```
