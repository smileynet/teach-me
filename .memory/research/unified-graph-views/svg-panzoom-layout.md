# Research — SVG Pan/Zoom + dagre layout polish (spike #275, Option C map view)

## Summary

For a static Preact SVG forest graph (~9–30 domain nodes, vendored dagre, no backend):

- **(A) Zoom/pan/fit: do it with viewBox math, no library.** Panning is mutating the
  viewBox `x/y`; zooming is scaling viewBox `w/h` around the cursor; fit-to-view is a
  one-line computation from dagre's output `graph.width/height` (plus a margin). This is
  ~40–60 lines of vanilla JS, zero deps, and it stays crisp at any zoom (vector, not
  raster). A library only earns its place if you need momentum/inertia, pinch gestures,
  and cross-browser touch normalization out of the box — `@panzoom/panzoom` (~3.7 kB gz)
  or `svg-pan-zoom` (~unminified ~30 kB / heavier) are the candidates, but both use CSS
  `transform` on a `<g>` rather than viewBox, which is a different model than a
  fit-to-view forest needs. **Recommendation: viewBox math.** [L4], [L6]
- **(B) dagre polish: the biggest wins are `rankdir:"LR"`, tight `nodesep`/`ranksep`,
  `align`, per-edge `weight`/`minlen`, and — critically — laying out each disconnected
  component (root tree) SEPARATELY then PACKING the bounding boxes.** dagre does NOT pack
  disconnected components; it spreads them across ranks, which is exactly the "islands
  float apart / dead space" pain. Curved edges come free from dagre's `edge.points` fed
  through a smoothing curve (Catmull-Rom / `curveBasis`) into an SVG `<path>`. [L4], [L6]

---

## (A) Zoom / Pan / Fit-to-view

### Core model: mutate the viewBox, don't scale pixels

An SVG `viewBox="minX minY width height"` maps a user-space rectangle onto the element's
rendered box. Panning and zooming are just arithmetic on those four numbers — the browser
re-renders vectors sharply at every scale, and hit-testing/anchors keep working. This is
the model recommended across the SVG community for graph canvases. [L6]

**Responsive setup (viewBox, not fixed px)** — the #1 fix for "fixed-px canvas doesn't
reflow":

```html
<!-- NO width/height attrs → element fills its CSS box; viewBox drives coordinate space -->
<svg viewBox="0 0 W H" preserveAspectRatio="xMidYMid meet"
     style="width:100%; height:100%; display:block">
```

- Omit fixed `width`/`height` attributes; set size in CSS (`width:100%`). The SVG then
  reflows with its container. (Same rule the project already applies to lesson SVGs:
  "viewBox only, responsive scaling via CSS" — `visual-teaching.md`.) [L1:established]
- `preserveAspectRatio="xMidYMid meet"` letterboxes the graph centered without distortion.

### Fit-to-view (fit graph to viewport)

dagre's layout writes `graph().width` and `graph().height` (total graph extent). Fit =
set the viewBox to that box plus a margin:

```js
function fitViewBox(gWidth, gHeight, pad = 20) {
  return [ -pad, -pad, gWidth + pad * 2, gHeight + pad * 2 ];
}
// state.viewBox = fitViewBox(g.graph().width, g.graph().height)
```

If you'd rather compute from actual rendered content (e.g. after adding labels that
overflow node boxes), use `svgEl.getBBox()` which returns `{x,y,width,height}` of the
drawn geometry — same four numbers, feed straight into the viewBox. Either way it's a
one-liner; no library needed. [L6], [L4]

### Zoom toward the cursor (the only non-trivial bit)

Naive zoom scales `w/h` and drifts the content. To keep the point under the cursor fixed,
convert the pointer to user-space, scale, then re-anchor:

```js
function zoomAt(vb, clientX, clientY, factor, svgEl) {
  const rect = svgEl.getBoundingClientRect();
  // pointer as a fraction of the rendered box → user-space coords
  const px = vb[0] + (clientX - rect.left) / rect.width  * vb[2];
  const py = vb[1] + (clientY - rect.top)  / rect.height * vb[3];
  const w = vb[2] * factor, h = vb[3] * factor;          // factor<1 = zoom in
  return [ px - (px - vb[0]) * factor,
           py - (py - vb[1]) * factor, w, h ];
}
// wheel: e.preventDefault(); vb = zoomAt(vb, e.clientX, e.clientY, e.deltaY>0?1.1:0.9, svg)
```

Clamp scale to a min/max (e.g. 0.2×–5× of the fit box) so users can't lose the graph. [L6]

### Pan (drag)

```js
// pointerdown: store start client x/y + start viewBox
// pointermove (while dragging): translate client delta into user-space delta
const dx = (start.cx - e.clientX) / rect.width  * vb[2];
const dy = (start.cy - e.clientY) / rect.height * vb[3];
vb = [ start.vb[0] + dx, start.vb[1] + dy, vb[2], vb[3] ];
```

Use Pointer Events (`pointerdown/move/up` + `setPointerCapture`) so mouse, touch, and pen
all work through one code path. In Preact, keep `viewBox` in a signal/state and render
`viewBox={vb.join(' ')}`; the diff is a single attribute update per frame. [L6]

### Library comparison (if you decide interactivity budget justifies a dep)

| Option | Size (gzip) | Model | Fit-to-view | Verdict for this task |
|--------|-------------|-------|-------------|-----------------------|
| **viewBox math (DIY)** | 0 kB | viewBox mutation | trivial (one line from dagre width/height) | **Recommended** — vector-crisp, vendored-free, ~50 LOC |
| `@panzoom/panzoom` (timmywil) | **~3.7 kB** | CSS `transform` on element | manual | Smallest lib; but CSS-transform model, not viewBox; adds momentum/pinch | 
| `anvaka/panzoom` | larger (kinetic engine) | transform matrix, DOM+SVG | `zoomAbs`/`showRectangle` | Nice inertia; heavier; overkill for 30 nodes |
| `svg-pan-zoom` (bumbu) | heaviest (~30 kB+ unmin) | wraps SVG in a viewport `<g>` transform | `.fit()` + `.center()` built-in | Most "batteries included" incl. `.fit()`, but old, larger, transform-based |

Sizes: `@panzoom/panzoom` self-reports **"~3.7kb gzipped"**; `svg-pan-zoom` is the largest
of the set (full-featured, wraps the SVG in a transform viewport with built-in `.fit()`
and `.center()` you'd otherwise write yourself). [L4:npm], [L4:github]

**Why DIY wins here:** the map is small and static, you already have dagre's exact
`width/height` for a perfect fit, and viewBox keeps SVG anchors/`getBBox`/arrowheads
honest. Libraries that use CSS `transform` on a `<g>` (both panzoom variants) fight the
"fit an unknown-size graph into the viewport" use case — you'd still compute the fit
math yourself. Only reach for `svg-pan-zoom` if you specifically want its bundled
`.fit()/.center()/.zoom()` control-panel UX and don't mind the weight.

---

## (B) dagre layout polish for a small multi-root forest

dagre output you consume: each node gets `{x,y,width,height}` (x/y = CENTER); each edge
gets `points: [{x,y}...]` (polyline through bend/control points, clipped to node borders);
the graph gets total `{width,height}`. Configure via `g.setGraph({...})`. [L4]

### The knobs (dagre graph options)

| Option | Default | Tune to | Effect |
|--------|---------|---------|--------|
| `rankdir` | `TB` | **`LR`** | Left→right reads like a roadmap; fans widen horizontally (usually better for wide sibling fan-out than tall TB). [L4] |
| `nodesep` | 50 | **~20–30** | Horizontal gap between nodes in the same rank — lower = tighter, less dead space. [L4], [L6:argdown ranksep/nodesep 0.2] |
| `ranksep` | 50 | **~30–50** | Gap between ranks — lower packs tiers closer. [L4] |
| `edgesep` | 10 | lower | Gap between parallel edges. [L4] |
| `align` | undefined | **`UL`/`DL`** | Aligns nodes within ranks up/down-left — reduces ragged staggering, straighter columns. [L4] |
| `ranker` | `network-simplex` | keep `network-simplex` (best tiers); `tight-tree` for compact trees | Tier-assignment algorithm; network-simplex minimizes total edge length = tightest. [L4], [L8] |
| `marginx/marginy` | 0 | small pad | Adds a graph-level margin (or handle padding in the viewBox instead). [L4] |
| `acyclicer` | undefined | `greedy` if cross-edges cause backward arrows | Removes a feedback-arc set so cyclic `leads_to` edges don't point "backward". [L4] |

Per-edge knobs to fix the "edges point backward / shared-child" pain:

- `edge.weight` (default 1): **raise on structural parent edges** so dagre makes them
  shorter/straighter and lays the hierarchy out cleanly; leave `leads_to` edges at weight
  1 so they bend around instead of distorting the tree. [L4]
- `edge.minlen` (default 1): raise to push a target further down-rank when a shared child
  is being pulled up next to its parent. [L4]
- `edgeLabelSpace: false` in layout opts removes dummy label nodes if you don't need edge
  labels — tighter layout. [L6:github dagre fork]

### THE key fix — pack disconnected components (kill the dead space)

dagre does **not** pack disconnected subgraphs; it lays all components in one coordinate
space and spreads them across shared ranks, which is the root cause of "root trees float
apart / islands waste space." The standard remedy:

1. **Split** the forest into connected components (union-find over parent + edges, or
   graphlib's `components(g)`).
2. **Lay out each component separately** with its own dagre graph → each yields its own
   `{width,height}` bounding box.
3. **Pack the boxes** yourself with a simple shelf/row bin-packing (sort by height, place
   left→right, wrap to a new row when the row width exceeds a target ≈ √(total area) or
   the container aspect), then **offset** every node/edge point in a component by its
   box's packed origin.
4. Recompute the overall `{width,height}` from the packed extent → feed fit-to-view.

This turns N floating trees into a compact tiled forest with minimal dead canvas. (dagre
has no built-in `pack`; cytoscape/ELK expose packing options, but for ≤30 nodes a 20-line
shelf packer is simpler than adding ELK.) [L4], [L2:cytoscape-dagre]

Isolated single-node "islands" pack into the same shelf as tiny boxes — no special case.

### Curved edges (from dagre points)

dagre already returns smooth-ish polylines in `edge.points` (border-clipped + bend
points). Two levels of polish:

1. **Cheap/robust:** join points as a polyline `M x0 y0 L x1 y1 L …` — orthogonal-ish,
   always correct.
2. **Curved:** feed `points` through a smoothing curve generator to emit an SVG `<path>`
   `d`. With d3-shape (or a tiny hand-rolled Catmull-Rom→Bézier), `d3.line().curve(
   d3.curveBasis)(points)` produces the classic smooth dagre look. The historical
   dagre-d3 renderer did exactly this via `lineInterpolate:'basis'` (== `curveBasis`).
   A `curveBasis`/Catmull-Rom pass over 3–7 dagre points gives smooth edges without new
   layout cost. If avoiding a d3 dep, a ~15-line Catmull-Rom-to-cubic-Bézier function
   over the points array emits the same `d`. [L3:d3], [L6:so dagre-d3 basis]

**Encoding parent vs leads_to** (spike question 2), cheap to layer on the path:
- parent (structural): solid stroke, `--svg-neutral`/`--svg-primary`, standard arrowhead,
  higher `weight`.
- leads_to (navigational): dashed stroke (`stroke-dasharray`), `--svg-warning` or a
  distinct hue, open/smaller arrowhead, weight 1. Add a small inline legend. Color must
  not be the only signal — pair with dash style (project accessibility rule). [L1:project]

### Suggested starting config

```js
g.setGraph({
  rankdir: "LR",
  nodesep: 24,
  ranksep: 40,
  edgesep: 10,
  align: "UL",
  ranker: "network-simplex",
  marginx: 8, marginy: 8,
});
// parent edges: g.setEdge(a,b,{weight:3});  leads_to: g.setEdge(a,b,{weight:1});
// then: layout each component separately → shelf-pack boxes → offset points → fit viewBox
```

---

## Sources

- [L4:verified] dagre wiki — Configuring the Layout (rankdir, nodesep, edgesep, ranksep, align, ranker, marginx/y, acyclicer; edge weight/minlen/labelpos; output node x/y = center, edge `points`, graph width/height). https://github.com/dagrejs/dagre/wiki — fetched, config table read directly.
- [L4:reported] dagre repo. https://github.com/dagrejs/dagre
- [L4:npm] `@panzoom/panzoom` — "Panzoom is a small library (~3.7kb gzipped)…" (CSS transforms). https://www.npmjs.com/package/@panzoom/panzoom ; repo https://github.com/timmywil/panzoom
- [L4:reported] `svg-pan-zoom` (bumbu) — cross-browser SVG pan/zoom, built-in `.fit()/.center()`; largest of the set. https://github.com/bumbu/svg-pan-zoom
- [L6:reported] `anvaka/panzoom` — kinetic pan/zoom for DOM+SVG (`zoomAbs`, `showRectangle`). https://github.com/anvaka/panzoom
- [L6:reported] SO — "How to zoom and scroll an <svg> element" (viewBox pan/zoom pattern). https://stackoverflow.com/questions/76644219/how-to-zoom-and-scroll-an-svg-element
- [L6:reported] SO — "Manipulate SVG viewBox with JavaScript (no libraries)". https://stackoverflow.com/questions/10085123/manipulate-svg-viewbox-with-javascript-no-libraries
- [L6:reported] SO — "Centering on a specific point when zooming using SVG viewBox". https://stackoverflow.com/questions/74067159/centering-on-a-specific-point-when-zooming-using-svg-viewbox-with-arbitrary-init
- [L6:reported] argdown docs — closely-packed layout via `ranksep:0.2 nodesep:0.2 concentrate:true` (GraphViz analogue of dagre nodesep/ranksep). https://argdown.org/guide/changing-the-graph-layout.html
- [L8:reported] Medium — "Understanding How Dagre.js Layout Works (Ranker: network-simplex)". https://medium.com/@angeloarcillas64/understanding-how-dagre-js-layout-works-ranker-network-simplex-5a4459b011c2
- [L6:reported] SO — "Dagre-D3 graph. Can edge path be customized?" (`lineInterpolate:'basis'` = curved edges). https://stackoverflow.com/questions/29942605/dagre-d3-graph-can-egde-path-be-customized
- [L4:verified] D3 — d3-shape curve (curveBasis / Catmull-Rom for smoothing polyline points into an SVG path). https://d3js.org/d3-shape/curve
- [L2:reported] cytoscape.js-dagre — dagre-as-a-layout notes (component/packing context). https://github.com/cytoscape/cytoscape.js-dagre
- [L1:established] Project steering `visual-teaching.md` — SVG accessibility/responsive rule (viewBox only, no fixed width/height; color must not be the sole signal).
