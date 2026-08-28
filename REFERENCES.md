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
