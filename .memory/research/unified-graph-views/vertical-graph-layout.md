# Vertical Graph/Tree Layout for a Shallow Wide Hierarchy

Target: 9 nodes, depth 0–1 (one root tier + one child tier), parent/child edges plus a few cross `leads_to` edges, rendered on a **portrait, vertically-scrolling** web canvas.

## Summary

- **Use a top-to-bottom (TB / `rankdir=TB`) layered layout, not left-to-right (LR).** TB is the canonical hierarchy orientation: depth = vertical position, so the parent→child relation reads as "above → below," which is what viewers expect from a tree/org-chart. LR rotates depth onto the horizontal axis, which fights a portrait canvas (a shallow-but-wide tree becomes wide-and-short — exactly the wrong aspect for a tall narrow viewport) and weakens the "descent" metaphor. [Established]
- **The wide tier (siblings) should span the horizontal axis; depth grows down the scroll.** A depth-0/1 tree is *shallow and wide* — TB puts the many siblings across the width (1 short rank) and uses only ~2 vertical bands, which is compact. But on a *narrow portrait* canvas, 8 siblings on one row will overflow width and shrink to unreadable. Prefer **multi-column wrapping of the sibling tier** (grid/wrapped rank) or a compact tree that lets siblings stack, trading a little vertical scroll (which is free in portrait) for readable node sizes. [Inferred from layout mechanics + aspect-ratio-constrained layout research]
- **Prefer a dedicated tree layout over a general DAG/Sugiyama layout when the structure is *mostly* a tree.** Tree layouts (spanning-tree based, e.g. d3 `tree`/`cluster`, reingold–tilford) are tidier, more compact, and more predictable for parent/child data. Reserve full DAG layout (dagre/Sugiyama layered) for when cross edges are structurally important. With only a *few* `leads_to` cross edges, the right move is: **lay out the spanning tree, then overlay the cross edges as secondary (styled/curved) links.** This is the standard "extract a spanning tree + draw the few non-tree edges on top" pattern. [Established]
- **Do not rely on LR for a portrait canvas.** Empirically, reading direction interacts strongly with comprehension, and Western readers scan left→right — but for *hierarchies* the dominant, expected mapping is still vertical (root at top). Flipping to LR to "use the reading direction" mainly helps horizontal *process/flow* diagrams, not depth hierarchies, and it directly conflicts with a tall narrow viewport. [Established]

## Details

### TB vs LR for parent→child comprehension

- The hierarchy convention is root-on-top, children-below; standard hierarchical (Sugiyama-style) layouts default to top-to-bottom and this "typical hierarchical layout, with the root on top, is preferred due to its performance" for readability of hierarchies (arXiv, *Shape Change Enhancing Hierarchical Layout for Pairwise Comparison of DAGs*). TB makes rank (depth) legible as a vertical stack, which is the mental model for parent/child. [Established]
- Diagram *orientation* measurably changes comprehension. A UCSB/Vanderbilt eye-tracking study on phylogenetic trees found subjects were **more accurate** with one diagonal orientation than the mirror orientation of the *same* information — two diagrams with identical content are "not necessarily equivalent in terms of how the information is interpreted," and reading behavior (left→right in Western culture) interacts with the layout's dominant line. Takeaway for us: orientation is not cosmetic; pick the one that matches both the viewport and the reader's scan, and for a hierarchy on a portrait canvas that is TB (depth down the scroll). [Reported — single study, eye-tracking, BioScience 2012]
- Business-process-modeling research explicitly notes the LR-vs-TB flow-direction convention "is barely discussed" and most recommendations are "neither based on scientific claims nor on empirical evidence," and follow-up experiments found readers "adapted well to uncommon reading directions." So there is **no strong empirical mandate for LR**; the decision should be driven by structure (hierarchy → vertical) and canvas (portrait → vertical), not a belief that LR is more readable. [Reported — WU Vienna ICSOFT-EA'14 / EMISA'15]

### Tall-not-wide layouts for a shallow, wide tree

- A depth-0/1 tree is inherently *wide* (many siblings) and *short* (2 ranks). TB gives you a short-but-wide picture; LR gives you a wide-but-short picture — **both are landscape-shaped**, which is the opposite of what a portrait canvas wants. To make it *tall-not-wide* you must break the wide tier across multiple rows:
  - **Wrap the sibling row into a grid** (e.g., 2–3 columns of children), so the child tier occupies several vertical rows instead of one long horizontal row. Depth still reads top→down (root above the grid). This converts free vertical scroll into readable node width. [Inferred]
  - **Compact/tidy tree layouts** (Reingold–Tilford, d3 `tree`) minimize width and are the natural fit; for a portrait target, choose the tree algorithm's vertical orientation and let it grow downward. [Established]
- Orthogonal/aspect-ratio-constrained layout research targets exactly this problem — arranging nodes to fit a desired bounding-box aspect ratio ("Aspect Ratio Constrained Orthogonal Layout," arXiv). If a library exposes an aspect-ratio or node-wrap constraint, set it to portrait rather than accepting the algorithm's default landscape spread. [Established]
- Practical dagre/Cytoscape note: `rankdir` accepts `TB | BT | LR | RL`; for a vertical tree use `TB` (or `BT` for tips-up). LR/RL are the horizontal variants to avoid here. (Graphviz/dagre/cytoscape-dagre docs.) [Verified — library docs]

### Tree layout vs DAG layout — when to choose which

- Two classic strategies: **(a) spanning-tree extraction** (lay out a tree, ignore/overlay non-tree edges) vs **(b) DAG edge-crossing minimization** (Sugiyama layered, e.g. dagre/dot). The Eurographics VisSym'00 comparison studies exactly this tradeoff. [Established]
- Decision rule for *this* data (predominantly parent/child, a few `leads_to`):
  - **Choose a tree layout** — it is tidier, more compact, and gives stable, predictable positions that match the parent/child data. A pure DAG layout would over-engineer a 9-node, depth-1 structure and can spread nodes to satisfy crossing minimization it doesn't need.
  - **Handle the few cross edges as an overlay**: topologically separate the spanning tree from the "forward-like" cross edges and draw the latter as secondary styled/curved links on top of the tree (the standard technique for single-root DAGs; see SO discussions on extending tree layout to DAGs by separating tree edges from forward edges). This keeps the tree's clarity while still showing `leads_to`. [Established]
  - Switch to a **full DAG/Sugiyama layout only if** cross edges become numerous or structurally load-bearing (multiple parents, real merges) — at that point crossing-minimization earns its cost. With "a few" cross edges it does not. [Established]

### Recommendation for the 9-node portrait canvas

1. Layout: **TB tree** (root at top), spanning-tree based.
2. Wide child tier: **wrap siblings into a 2–3 column grid** so the picture is tall, not wide, and nodes stay readable in a narrow viewport.
3. Cross edges: draw the few `leads_to` links as **secondary curved overlays** on top of the tree, visually distinct from parent/child edges.
4. Avoid `rankdir=LR` — it produces a landscape shape that fights the portrait canvas and does not improve hierarchy comprehension.

## Sources

- [A Shape Change Enhancing Hierarchical Layout for the Pairwise Comparison of DAGs](https://arxiv.org/html/2406.05560v1) — arXiv; "typical hierarchical layout, with the root on top, is preferred." [L4]
- [Psychologist studies the effects of diagram orientation on comprehension](https://phys.org/news/2012-09-psychologist-effects-diagram-comprehension.html) — UCSB/Vanderbilt eye-tracking (BioScience 2012); orientation changes comprehension of identical content; LR reading bias interacts with layout. [L4/L5 popular summary of L4 study]
- [Modeling flow direction of business process models (ICSOFT-EA'14)](http://wi.wu.ac.at/home/mark/publications/icsoft-ea14.pdf) — LR-vs-TB convention "barely discussed," recommendations "neither based on scientific claims nor empirical evidence." [L4]
- [Findings from an Experiment on Flow Direction of Business Process Models (EMISA'15)](https://complex.wu.ac.at/nm/strembeck/publications/emisa15.pdf) — readers "adapted well to uncommon reading directions." [L4]
- [Aspect Ratio Constrained Orthogonal Layout](https://arxiv.org/html/2603.29618v1) — arXiv; laying out graphs to a target bounding-box aspect ratio. [L4]
- [Spanning-tree vs edge-crossing-minimization layout comparison (VisSym'00)](http://diglib.eg.org/bitstream/handle/10.2312/VisSym.VisSym00.003-012/003-012.pdf) — Eurographics; the two core strategies and their tradeoffs. [L4]
- [Drawing DAGs: minimizing edge crossing / Directed Acyclic Graph with Hierarchical Layout](https://stackoverflow.com/questions/2853093/) and [SO revision on topological split into tree + forward edges](https://stackoverflow.com/revisions/79821761/1) — extract spanning tree, overlay non-tree/forward edges. [L6]
- [Graphviz rankdir docs](https://graphviz.org/docs/attrs/rankdir/) / [Cytoscape.js dagre vertical tree (SO)](https://stackoverflow.com/questions/53231400/can-cytoscape-js-with-dagre-layout-draw-a-vertical-tree) — `rankdir: TB|BT|LR|RL`; use `TB` for a vertical tree. [L4/L6]
