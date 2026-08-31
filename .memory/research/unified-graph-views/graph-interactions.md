# Graph Interactions — What Makes a SMALL Node-Link Graph Useful (not Decorative)

Research for spike #275 (iterate Option C: dagre MAP view as the secondary "how domains
connect" view, ~9–30 domain nodes, Preact + SVG, static site, no backend).

## Summary

The literature is consistent: a *static* node-link graph is decoration; interactivity is what
converts it into an exploration tool. But the classic guidance (Shneiderman's "overview first,
zoom and filter, then details on demand") and the anti-clutter research (the "hairball") are
written for **large** graphs (thousands+ of nodes). For a **small** graph (9–30 nodes) most of
that machinery is unnecessary — the whole graph already fits on screen, so "overview" is free and
"zoom to see anything at all" is not the problem it is at scale.

That inverts the priority list. For a small graph the interactions that pay off are the ones that
answer **"what connects to what, and where do I go next"** with near-zero effort:
**hover-to-highlight-neighbors** and **detail-on-demand (tooltip/label + click-through link)**
are the highest-value, lowest-cost additions. **Fit-to-view + responsive viewBox** is worth it
mainly as a layout-quality fix (kills the dead-canvas / islands-drift pain), not as a navigation
feature. **Zoom/pan** and **click-to-focus/expand** are low value for a graph that already fits —
they solve a problem this graph doesn't have, and add code + failure modes. **Filter by edge type**
is worth it *only because this graph has two semantically distinct edge types* (parent vs
leads_to) — but a static **legend + visual encoding** (line style/color/arrowhead) may deliver
80% of the value at 10% of the cost; make the filter an enhancement, not a requirement.

The single biggest "useful vs decorative" lever for a small graph is not an interaction at all —
it's **visual encoding + a legend** so each edge and node *means* something at a glance
(Tom Sawyer, Cambridge Intelligence). Interactions are the second lever, and only a couple of
them earn their place at this size.

## Ranked interaction list (is it worth it for a ~9–30 node graph?)

### Tier 1 — Do it (high value, low cost, directly fixes "decorative")

1. **Hover-neighbor-highlight (fade the rest)** — WORTH IT. ★★★★★
   On hover of a node, highlight it + its incident edges + adjacent nodes, and dim (lower opacity)
   everything else. This is the single most-recommended small-graph interaction: it answers "what
   is this connected to?" instantly without changing layout or requiring a click. Cheap in SVG
   (toggle a class / opacity on a precomputed neighbor set). Well-trodden pattern (many D3 recipes;
   yWorks "Exploring Relations"). Do the reciprocal on hovering an *edge* too (highlight its two
   endpoints). For teach-me: hovering a domain shows its parent + its leads_to targets lit up —
   exactly the "how domains connect" question the MAP view exists to answer.

2. **Detail-on-demand: tooltip + click-through** — WORTH IT. ★★★★★
   Shneiderman's "details on demand" — keep the node face minimal (label + a progress/sub-map
   glyph), reveal more (description, counts, "open this domain") on hover-tooltip and on click
   navigate to the domain/sub-map. This is what makes the graph a *navigation surface* rather than
   a picture. At 9–30 nodes you can afford always-on labels (no de-clutter needed), so "detail on
   demand" here means the *secondary* info and the click target, not the label itself.

3. **Legend + visual encoding for the two edge types (parent vs leads_to)** — WORTH IT. ★★★★★
   (Encoding, not strictly an "interaction," but the top useful-vs-decorative lever.) Distinct
   line style + color + arrowhead for structural (parent) vs navigational (leads_to) edges, plus
   a small always-visible legend. Without this the graph is a tangle of identical lines =
   decorative. With it, every edge carries meaning. Node encoding likewise: shape/badge for
   "has sub-map" and a progress ring/fill for completion.

### Tier 2 — Worth it, but as polish / conditional

4. **Fit-to-view via responsive SVG `viewBox` (replace fixed-px canvas)** — WORTH IT as a *layout
   fix*, not a nav feature. ★★★★☆
   Compute the bounding box of all dagre-placed nodes and set `viewBox="minX minY W H"` with
   `preserveAspectRatio="xMidYMid meet"`, no fixed width/height, `width:100%;height:auto` in CSS.
   This directly kills the spike's stated pains (dead canvas space, islands drifting apart, no
   reflow) and makes it responsive/mobile-friendly — for free, no library. This is the highest-value
   item among the "zoom/pan/fit" family for a small graph. `viewBox` is "the single most important
   line for predictable scaling" (TheLinuxCode). Implement this; it's the one you clearly want.

5. **Filter by edge type (toggle parent / leads_to)** — CONDITIONAL. ★★★☆☆
   Because there ARE two edge meanings, letting the reader hide leads_to (see pure hierarchy) or
   hide parent (see suggested-next paths) is genuinely useful — filtering is a core "useful graph"
   feature (Tom Sawyer, Shneiderman's "zoom and filter"). BUT at 9–30 nodes a good legend +
   encoding (#3) already lets the eye filter. Ship encoding+legend first; add the toggle only if the
   combined graph still reads as busy. Low implementation cost (toggle edge visibility), so it's a
   reasonable stretch — just not required for "not decorative."

### Tier 3 — Skip / not worth it at this size

6. **Zoom & pan (free camera)** — SKIP for a small graph. ★★☆☆☆
   Essential for large graphs (Tom Sawyer, Cambridge Intelligence) but a graph that already fits
   on screen gains little; free pan/zoom mostly adds "lost in space," accidental scroll-hijack, and
   a "reset view" burden. Fit-to-view (#4) gives the good part (everything visible) without the
   cost. Optional: a single **"fit / reset" button** or pinch-to-zoom on mobile as a nicety — but
   don't build full pan/zoom as a core feature. (If you later add click-to-focus, a *scripted*
   zoom-to-node is different from free pan/zoom — see #7.)

7. **Click-to-focus / expand (collapse subtrees, ego-graph, animated zoom-to-node)** — SKIP /
   OVERKILL. ★★☆☆☆
   Collapsible nodes and focus+context are explicitly recommended for *dense/large* graphs to fight
   clutter (Tom Sawyer "collapsible nodes prevent excessive visual clutter"; focus+context lit).
   With 9–30 nodes there's no clutter to collapse and nothing hidden to expand — the whole graph is
   the overview. Click should simply **navigate** (open the domain) — that's #2, not a focus mode.
   Building expand/collapse or ego-graph here adds state + animation + a way to get confused, for a
   problem you don't have.

8. **Force-directed / physics interactivity, drag-to-reposition** — SKIP. ★☆☆☆☆
   Dagle already gives a stable hierarchical layout (good — "stable positions" is a usability win;
   force layouts wander between loads). Adding drag/physics reintroduces instability and the
   hairball dynamics that small-graph clarity depends on avoiding. Keep positions deterministic.

## Cross-cutting principles (why the ranking is what it is)

- **Static graph = decoration; interaction = tool** — the recurring thesis (Tom Sawyer: interactivity
  "transforms static node-link data into dynamic, navigable environments"). But the *cheapest*
  interactions (hover-highlight, detail-on-demand) capture most of that value at small scale.
- **Shneiderman's mantra ("overview first, zoom and filter, details on demand")** was designed for
  large spaces. For 9–30 nodes the "overview" and "zoom" stages are already satisfied by fitting
  the whole graph on screen — so invest in the **filter** (edge-type) and **details-on-demand**
  stages, and skip aggressive zoom.
- **The hairball is a large-graph failure mode** — clutter, over-plotting, "a failure of
  visualization" (Cambridge Intelligence; Medium). A 9–30 node graph won't hairball *if* you
  encode edge types distinctly and keep layout stable; the fix here is encoding + a legend, not
  de-clutter interactions.
- **Encoding must be functional, not arbitrary** — "color and size should serve a functional
  purpose" (Tom Sawyer best practices); "get encoding wrong and your chart becomes decoration"
  (TheLinuxCode). This is why #3 (legend + edge/node encoding) outranks most interactions.
- **Accessibility** — provide keyboard reach + ARIA labels for nodes/edges and an alternative
  text/tree view (Tom Sawyer accessibility section). For teach-me this is already satisfied: the
  TREE view is the accessible primary; the MAP is the secondary relationship view.

## Recommendation for spike #275 (concrete)

Build, in order: **(A) responsive `viewBox` fit-to-view** (fixes the layout pains, no lib) →
**(B) edge-type encoding + legend + node badges/progress** (the decorative→useful lever) →
**(C) hover-neighbor-highlight with fade** → **(D) click-to-navigate + hover tooltip**
(detail-on-demand). Treat **edge-type filter toggle** as an optional stretch after (B) proves
insufficient. Do **not** build free zoom/pan, expand/collapse, or drag/physics for this size —
they solve large-graph problems this graph doesn't have.

## Sources (with URLs)

- [L4:established] Tom Sawyer Software — "Interactive Graph Visualization: The Ultimate Guide"
  (2025). Core features: zoom & pan, node/edge highlighting, filtering & search, collapsible nodes;
  best practices (functional color/size, accessibility, mobile). https://blog.tomsawyer.com/interactive-graph-visualization
- [L4:established] B. Shneiderman — "The Eyes Have It: A Task by Data Type Taxonomy for Information
  Visualizations" (1996). The Visual Information-Seeking Mantra: overview first, zoom and filter,
  details on demand. https://eclass.uoa.gr/modules/document/file.php/DI453/PAPERS/Shneiderman_2003_The%20EyesHaveIt.pdf
  (ACM record: https://dl.acm.org/doi/10.5555/832277.834354)
- [L5:reported] Cambridge Intelligence — "Fixing Data Hairballs." Hairballs happen when you try to
  visualize everything in a richly connected graph; density hides patterns.
  https://cambridge-intelligence.com/blog/hairball-effect-in-graph-visualization/
- [L6:reported] Medium (H. Krishnan) — "Hairball Graph Problem." A hairball is "a failure of
  visualization" that obscures insights. https://medium.com/@harikrishnank497/hairball-graph-problem-a8ce62d324d5
- [L6:reported] yWorks — "Exploring Relations in a Diagram" (hover to see nodes in close relation via
  edges). https://www.yworks.com/pages/exploring-relations-in-a-diagram
- [L6:reported] Stack Overflow — hover-highlight neighbors patterns in force/node-link graphs
  (representative of the standard technique): 
  https://stackoverflow.com/questions/23067154/highlight-a-node-and-its-neighbour-node-in-force-directed-graph ;
  https://stackoverflow.com/questions/8739072/highlight-selected-node-its-links-and-its-children-in-a-d3-force-directed-grap
- [L4:established] MDN — SVG `viewBox` attribute (responsive scaling / camera).
  https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox
- [L6:reported] TheLinuxCode — "SVG viewBox: A Practical, Deep Guide to Scaling, Panning, and
  Responsive Behavior" (viewBox is the key line for predictable scaling/pan; camera-zoom via
  viewBox). https://thelinuxcode.com/svg-viewbox-attribute-a-practical-deep-guide-to-scaling-panning-and-responsive-behavior/
- [L6:reported] Stack Overflow — "How to zoom, pan, center and scale to fit on node click … set the
  viewBox attribute" (scripted fit/zoom via viewBox rather than a library).
  https://stackoverflow.com/questions/74674483/how-to-zoom-pan-center-and-scale-to-fit-on-node-click-both-for-the-clicked-nod
- [L6:reported] TheLinuxCode — "Advantages and Disadvantages of Data Visualization (2026)":
  "get encoding wrong and your chart becomes decoration." https://thelinuxcode.com/advantages-and-disadvantages-of-data-visualization-2026-an-engineers-field-guide/
- [L4:reported] Springer / Vis. Comput. Ind. Biomed. Art (2021) — "Dynamic graph exploration by
  interactively linked node-link diagrams and matrix visualizations": for sparse/small graphs,
  node-link diagrams are the efficient choice. https://link.springer.com/article/10.1186/s42492-021-00088-8

## Open questions / gaps

- No source gave a size-specific empirical cutoff for when zoom/pan starts paying off; the
  "skip zoom/pan for small graphs" ranking is INFERRED from the fits-on-screen argument + the fact
  that all zoom/pan advocacy in the sources is framed around large/dense graphs. Tentative, not
  measured.
- roadmap.sh / skill-tree / Cytoscape/ELK concrete prior-art examples weren't fetched in depth this
  pass (search surfaced general patterns, not a teardown). If a teardown is wanted, dispatch a
  follow-up specifically on "roadmap.sh interaction model" and "Cytoscape.js fCoSE small-graph
  demos."
