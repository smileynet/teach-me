# Visual Encoding — Two Edge Types + Node Status (Spike #275, MAP view iteration)

Research for the dagre node-link MAP view: how to visually distinguish **structural
parent/child** edges from **navigational `leads_to` / suggested-next** edges, and how to
encode node **progress** + **sub-map** flag — accessibly, with the least chrome.

## Summary

Three encoding channels reliably separate two edge semantics, and the established
convention across UML, ER/schema diagrams, and node-graph tooling is consistent:

- **Line style is the primary, color-independent discriminator.** SOLID = structural /
  identity-bearing relationship (parent→child); DASHED (or dotted) = a weaker,
  navigational / dependency / "dynamic" relationship (leads_to / suggested-next). This
  mapping is not arbitrary — it's the de-facto standard: DataJoint schema diagrams state
  the principle explicitly ("Solid lines mean the parent's identity becomes part of the
  child's identity. Dashed lines mean the child maintains independent identity"), UML uses
  solid for associations/generalization and dashed for dependencies, and Meshery's edge
  guide uses "dotted = dynamic connections." [DataJoint, StackOverflow-UML, Meshery]
- **Arrowheads encode direction, not type.** ISO 5807 and node-link convention: a
  triangular arrowhead at the target end means source→target. Use the SAME arrowhead shape
  on both edge types (direction is meaningful for both: parent→child *and* prereq→next).
  Do NOT try to overload arrowhead shape to also carry edge type — that's a third variable
  on a channel users read as "which way does this flow." [emergentmind/ISO5807, ResearchGate]
- **Color is a redundant reinforcement, never the sole signal.** WCAG 1.4.1 and every
  accessibility guide (Oracle, Penn State, W3C) require a second cue (line style, label,
  shape). Since line style already carries the type, color is free to *reinforce* it — but
  the graph must stay legible in grayscale.

Curved vs orthogonal: **straight/orthogonal edges are more readable; curves buy
aesthetics and overlap-reduction, not comprehension.** Only curve when two edges would
otherwise overlap or when you must visually separate the two edge families.

A **legend is required here** — the moment a viz uses more than one line type/color to
mean different things, a legend is standard practice (especially map-like relationship
views). Two edge semantics + node-status colors clears that bar.

## Encoding Recommendations

### Edge type: parent/child (structural) vs leads_to (navigational)

| Channel | parent/child (structural) | leads_to (suggested-next) | Rationale |
|---|---|---|---|
| **Line style** (primary) | **Solid** | **Dashed / dotted** | Matches DataJoint, UML, Meshery convention; readable in grayscale (color-independent) |
| **Stroke weight** | Slightly heavier (e.g. 2px) | Lighter (e.g. 1.5px) | Reinforces "structural = the backbone"; DataJoint uses thick-vs-thin solid for exactly this "strength of relationship" idea |
| **Color** (redundant) | Neutral/structural hue (e.g. `--svg-neutral` or `--svg-primary`) | Distinct accent (e.g. `--svg-success` = "where you can go next") | Reinforces, never sole. Green for leads_to reads as "forward / progression" |
| **Arrowhead** | Triangular, orient=auto, at child | Triangular, orient=auto, at target | SAME shape both types — arrowhead = direction only, not type (ISO 5807) |
| **Routing** | Orthogonal/straight (dagre points) | Curved *only if it would overlap a parent edge* | Straight = most readable; curve to disambiguate crossings |

Recommendation: **line style is the load-bearing distinction** (solid vs dashed).
Weight + color are redundant reinforcements. This survives colorblindness and grayscale
printing — the WCAG-safe design.

### Node encoding: progress + sub-map flag

Two independent attributes → two independent, non-color-primary channels:

- **Progress** — encode with a *shape/fill* cue, not color alone:
  - A **progress ring / arc** or a **fill bar** around/under the node (0–100%) is
    self-labeling and colorblind-safe (the arc length IS the value).
  - If using discrete states (not-started / in-progress / done), pair color with a
    **glyph or border**: e.g. done = solid check + filled; in-progress = half-fill;
    not-started = hollow/outlined. Color (gray→amber→green) reinforces but the
    fill/glyph carries it. (WCAG 1.4.1 — Oracle/Penn State/W3C.)
- **Sub-map flag** — encode with **shape or a decorator icon**, distinct from progress:
  - A **badge/icon** (e.g. a small "⊞" / folder / stacked-cards glyph) on the node, or a
    **double-border / drop-shadow "this expands" affordance**. Shape channel is orthogonal
    to the fill/color channel used for progress, so the two never collide.
  - Signal it as interactive (click-to-open the sub-map) — a decorator that reads as
    "there's more inside."

Keep to **one meaning per channel**: color→(reinforce)status, arc/fill→progress amount,
badge/border-shape→has-sub-map, node label→identity. Don't let color try to say both
"status" and "has sub-map."

### Legend

Include a small legend on the MAP view. It should show:
1. Solid line = "prerequisite / parent" (structural)
2. Dashed line = "suggested next" (leads_to)
3. Node status swatches WITH their glyph/fill (not just color chips) — mirror the
   color-not-alone rule in the legend itself.
4. Sub-map badge = "click to open sub-map"

Rationale: legends are the standard mechanism whenever >1 line type/color carries
distinct meaning, and they reduce clutter by moving labels off the canvas
(xdgov Data Design Standards; Carbon Design System). A single-series chart needs no
legend (UC Berkeley), but a two-edge-type relationship map is inherently multi-series.

### Curved vs orthogonal (readability)

- **Default to straight/orthogonal** dagre-routed edges — user studies find curved and
  animated links perform *worse* than straight links on graph-reading tasks; curves win
  only on aesthetics/interest, and orthogonality + collinearity measurably aid readability
  (ResearchGate "Effects of curves"; Monash InfoVis 2012; Xu et al. curved-edge study).
- **Curve selectively** to (a) separate the two edge families where a solid and a dashed
  edge run between the same pair or nearly overlap, and (b) route around nodes instead of
  through them. Curvature as a *disambiguation tool*, not a global style.
- For a small forest (~9–30 nodes) the readability cost of curves is low and the
  overlap-reduction benefit is real where components pack tightly — so: straight by
  default, gentle curve on conflict.

### Accessibility checklist (color-not-alone)

- [ ] Edge type distinguishable with color removed (solid vs dashed does this).
- [ ] Node status distinguishable with color removed (fill/arc/glyph does this).
- [ ] Sub-map flag distinguishable with color removed (badge/border-shape does this).
- [ ] Legend entries show the non-color cue, not just a color chip.
- [ ] SVG uses `role="img"` + `<title>` + theme `var(--svg-*)` (per project steering).

## Sources

- [DataJoint — Read Schema Diagrams](https://docs.datajoint.com/how-to/read-diagrams/) —
  [L4:verified] Explicit principle: **solid = identity-bearing structural relationship,
  dashed = independent-identity reference**; thick-vs-thin solid encodes relationship
  strength; arrowless direction via top-to-bottom layout. Fetched full page.
- [UML relationships: dashed vs solid line (StackOverflow)](https://stackoverflow.com/questions/26982886/uml-relationships-dashed-line-vs-solid-line/48819137) —
  [L6:reported] UML convention: solid = association/structural, **dashed = dependency**
  ("show how changes in one element might alter other elements"). (Snippet; page 403'd on fetch.)
- [Meshery — Edge Styles Guide](https://docs.meshery.io/guides/configuration-management/edges-guide/) —
  [L4:reported] "Dotted pattern = dynamic connections; arrowheads show direction of data
  flow or dependency" — tooling convention that arrowhead=direction, dash=relationship kind.
- [ISO 5807 Flowcharts Overview (EmergentMind)](https://www.emergentmind.com/topics/iso-5807-flowcharts) —
  [L2:established] Arrowheads strictly indicate flow direction, source→target.
- [A User Study on Visualizing Directed Edges in Graphs (ResearchGate PDF)](https://www.researchgate.net/publication/221515079_A_User_Study_on_Visualizing_Directed_Edges_in_Graphs) —
  [L4:established] Directed edge = polyline + triangular arrowhead at target (baseline convention).
- [Effects of curves on graph perception (ResearchGate)](https://www.researchgate.net/publication/302073539_Effects_of_curves_on_graph_perception) —
  [L4:established] "Curved and animated links … seem to be worse than straight links" for
  reading tasks; curves have aesthetic benefits only.
- [A User Study on Curved Edges in Graph Visualization (ResearchGate)](https://www.researchgate.net/publication/254256593_A_User_Study_on_Curved_Edges_in_Graph_Visualization) —
  [L4:established] Studies edge curvature impact vs straight segments (the conventional choice).
- [Marriott et al., "Memorability of visual features in network diagrams" / InfoVis 2012 (Monash PDF)](https://ialab.it.monash.edu/~mwybrow/papers/marriott-infovis-2012.pdf) —
  [L4:established] Symmetry, collinearity, **orthogonality** strongly aid readability.
- [WCAG 2.2 Understanding SC 1.4.1: Use of Color (W3C)](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) —
  [L2:verified] Information conveyed by color must also be available without color.
- [Providing Alternatives to Color Coding (Oracle)](https://docs.oracle.com/cd/F28299_01/pt857pbr3/eng/pt/tacs/task_ProvidingAlternativestoColorCodingtoConveyMeaning-ba7fc3.html) —
  [L4:established] "Do not use color as your only way to convey information; include a
  redundant clue" (shape/text/pattern).
- [Accessibility at Penn State — Color Coding](https://accessibility.psu.edu/color/colorcoding/) —
  [L4:established] Use a second mechanism (different shapes or text labels) alongside color.
- [Data Visualization Standards — Legends (xdgov)](https://xdgov.github.io/data-design-standards/components/legends) —
  [L4:established] Legends are used "when there is more than one color or line type" —
  most common in maps; moving labels off-canvas reduces clutter.
- [Carbon Design System — Legends](https://carbondesignsystem.com/data-visualization/legends/) —
  [L4:reported] Legend placement/clustering guidance.
- [UC Berkeley Library — Data Viz Design](https://guides.lib.berkeley.edu/data-visualization/design) —
  [L4:reported] "If you only have one data category, there is no need for a legend"
  (corollary: >1 category → legend).

## Open Questions

- Discrete status states vs continuous progress %: does the map need a fill-arc (continuous)
  or is a 3-state glyph (not-started/in-progress/done) enough? (Depends on what the tree
  view already shows — avoid duplicating fidelity.)
- Should `leads_to` edges be filterable/toggle-able (show structure only) — pairs with the
  legend as an interactive filter, per the "interactive graph > static decoration" finding.
