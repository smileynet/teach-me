---
id: "379"
title: "Fix graphviz version gap: draw-diagram --backend graphviz fails on svg_inline"
status: done
blocked_by: []
tags: ["tooling"]
---

# Fix graphviz version gap: `draw-diagram --backend graphviz` fails on `svg_inline`

`tools/draw-diagram.py --type graph --backend graphviz` is broken on this machine
(and any host with an older system graphviz): the tool requests the `svg_inline`
output format, but the installed `dot` is **2.44.0**, and `svg_inline` was added in
graphviz **~7.x**. The command dies with an unsupported-format error, so the graphviz
auto-layout backend is unusable for cyclic / back-edge diagrams project-wide.

Surfaced during the lesson-371 build (the-universal-serving-pipeline): the loop
diagram needed a back-edge, the ticket AC called for `--backend graphviz`, but the
backend couldn't run. Worked around by hand-authoring the inline SVG (matching the
gltf-format house pattern), flagged as an honest deviation in #371. Every future
lesson that wants graphviz auto-layout (state machines, 9+ node graphs, cyclic
graphs — see `visual-teaching.md` § Diagram Selection) will hit the same wall.

## What to build

Pick ONE of:
1. **Upgrade graphviz to ≥7.x** in the project toolchain (mise-managed, so the version
   is pinned and reproducible on every clone/CI runner), OR
2. **Fall back gracefully in `draw-diagram.py`** — detect the graphviz version /
   unsupported `svg_inline`, and emit plain `svg` (then post-process to inline) when
   the newer format isn't available, so old and new graphviz both work.

Prefer (1) if mise can pin a modern graphviz cleanly; (2) is the robust fallback if the
target environments can't all get ≥7.x.

## Acceptance criteria

- [x] `mise run draw -- --type graph --backend graphviz --data '{...}'` produces valid
      inline SVG on this machine (graphviz 2.44.0 present) without error
- [x] The output SVG is accessible (`role="img"` + `<title>`) and responsive (viewBox, no
      fixed width/height) — matching the builtin backend's contract
- [x] If upgrading: the graphviz version is pinned in `mise.toml` and `mise run doctor`
      reports it; if falling back: a unit/smoke check exercises the old-graphviz path
      — chose the fallback (portable across all environments); smoke-tested a back-edge graph
- [x] `mise run verify` passes

## Design source

- `tools/draw-diagram.py` (the `svg_inline` format request on the graphviz object)
- `.kiro/steering/visual-teaching.md` § Diagram Selection (when graphviz backend is required)
- #371 Resolution section (the deviation record and environment-gap note)

## Resolution

Fixed via **option 2 (graceful fallback)** rather than upgrading graphviz — the fallback
is portable across every environment (old system graphviz, CI runners, other clones) and
needs no binary pin that may not build on all platforms.

**Change** (`tools/draw-diagram.py`):
- Added `_svg_format(version)` — returns `svg_inline` when graphviz major ≥ 6 (the version
  that introduced the format), else plain `svg`. `svg_inline` is added in graphviz 6.0; the
  only difference from `svg` is the omitted XML/DOCTYPE preamble.
- `diagram_graphviz` now calls `format=_svg_format(version)` instead of the hardcoded
  `svg_inline`.
- Strip both `<?xml?>` and `<!DOCTYPE>` from the rendered SVG so the plain-`svg` path
  yields the same clean inline SVG as `svg_inline`.

**Verified:** `--type graph --backend graphviz` with a back-edge graph (the exact 371 case)
now produces valid accessible inline SVG on graphviz 2.44.0; the builtin backend is
unchanged; `mise run verify` passes.

**Orthogonal limitation noted (NOT this ticket):** the graphviz backend passes `var(--svg-*)`
CSS custom properties as node fill/stroke colors, which `dot` can't consume — it renders them
black and warns. This is why the builtin backend is preferred and lessons hand-author SVG. It
exists at every graphviz version and is independent of the format gap fixed here. File a
separate ticket if the graphviz backend needs theme-var colors.
