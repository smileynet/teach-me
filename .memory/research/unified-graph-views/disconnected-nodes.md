# Disconnected Nodes (Islands) in Node-Graph / Forest Visualizations

## Summary

For a forest/node-graph view where some nodes have **no edges** ("islands"/orphans),
the established practice splits by *why* the node is disconnected:

- **Layout mechanics:** never let a general-purpose layout (force-directed, dagre)
  freely place islands — they drift to corners or blow the bounding box, wasting
  canvas. Lay each connected component individually, then **pack the components**
  (and the singletons among them) into a compact grid/array so the canvas isn't
  wasted [L4:established].
- **UX placement:** the field's strongest aesthetic rule is *maximize distance
  between unconnected nodes* — proximity implies a relationship that doesn't exist
  [L4:established, Williams CS326]. That argues **against** scattering islands
  inline among the connected clusters. Two clean options that both satisfy it:
  (a) pack islands into their own dedicated region of the same canvas (a labeled
  "no connections" tray/row), or (b) move them to a **separate list/sidebar**.
- **Duplication (graph + sidebar):** showing the same island in both the canvas and
  a sidebar list is generally discouraged — it doubles the node's identity and
  invites "are these two different things?" confusion. Prefer **one home** per node;
  if a sidebar lists islands, don't also render them as canvas nodes (and vice
  versa). A sidebar that *indexes* all nodes (islands included) is fine as long as
  it reads as navigation, not as a second copy of the graph.

**Recommendation for a forest map:** don't inline-scatter islands. Either pack them
into a labeled corner region of the canvas (keeps everything spatial, one home per
node) or list them in a sidebar and *omit* them from the canvas. Pick one; don't do
both for the same node.

## Details

### 1. Inline vs. separate — the core trade-off

- **Aesthetic principle (why inline scattering hurts):** "Maximize the distance
  between unconnected nodes. If two unconnected nodes are placed near one another,
  the reader can be confused into thinking that they are somehow related when in
  fact there is no connection." — Williams CS326 graph-layout heuristics
  [L4:established]. Islands dropped inline next to a cluster read as "part of that
  cluster." This is the strongest argument for corralling them, whether in a canvas
  region or a sidebar.
- **What layouts do by default (the failure mode):** force-directed layouts
  (cose-bilkent, Fruchterman-Reingold) push disconnected nodes to the periphery /
  upper-right corner, "far away from the connected nodes, which looks not good"
  [L6:reported, SO cose-bilkent]. NetworkX's default draw "places nodes awkwardly
  when there are disconnected nodes" [L6:reported]. So *doing nothing* gives you the
  worst inline outcome — scattered, distant, space-wasting.

### 2. Avoiding wasted canvas from disconnected components

- **Lay out components separately, then pack them.** The canonical SO answer:
  "(b) Compute the layout for each component individually, and then arrange
  components in visually pleasing ways w.r.t. each other" [L6:established]. Option
  (a) — only plot the largest component — is available when small components are
  noise, but it *removes* nodes, which a forest map usually can't do.
- **Component packing is a studied problem.** Freivalds, Dogrusoz & Kikusts,
  *Disconnected Graph Layout and the Polyomino Packing Approach* (GD 2001): lay out
  each component, then pack the components' bounding shapes. Their polyomino
  representation (vs. plain rectangles) "produces much more compact and uniform
  drawings than previous methods" — i.e. the whole point is to *not waste space*
  between disconnected pieces [L4:established]. Singleton islands are just
  1-node components in this scheme.
- **Practical tooling knobs:** Graphviz exposes `packmode` (e.g. `array` / `array_c`)
  to arrange loose nodes/components into a compact grid beside the main graph rather
  than letting them float [L4:reported, graphviz forum]. Cytoscape's
  layout-utilities places disconnected nodes "an ideal edge length away from a
  neighbor" with a random offset to avoid overlap [L4:reported]. The recurring
  answer to "align loose nodes beside the main graph" is: put them in a packed
  array region, not interleaved.

### 3. dagre specifically (relevant if the forest uses dagre)

- dagre is a **DAG/tree** layout. Fed multiple trees + independent nodes, it "arranges
  the roots horizontally, which makes the nodes and labels become very small" — the
  independent nodes stretch the layout and shrink everything [L6:reported, SO 32041577].
  React-Flow + dagre users hit overlap/awkward placement for disconnected graphs and
  end up writing custom placement [L6:reported, SO 79359437].
- **Pattern that works with dagre:** run dagre per connected component, then position
  the resulting component boxes yourself (grid/row packing), and place singleton
  islands in a dedicated packed row/tray. This mirrors the "layout each component,
  then pack" advice above and keeps dagre doing what it's good at (each tree)
  without letting islands distort the ranks.

### 4. Duplication (graph + sidebar) — confusing?

- No source endorses rendering the *same* node both as a canvas node and as a
  sidebar entry that looks like another node. The identity/proximity concern from
  the Williams heuristic extends here: two visual instances of one node invite
  "are these the same or related?" ambiguity.
- Safe patterns:
  - **Sidebar-as-index:** a list panel that navigates to nodes (including islands)
    is fine — it reads as a table of contents, not a duplicate graph. Islands may
    then be *omitted* from the canvas or shown once in a canvas tray, not both.
  - **Canvas tray:** keep everything spatial by giving islands a labeled region
    ("Unconnected" row along one edge), packed compactly. One home per node, no
    sidebar duplication.
- **Rule of thumb:** each node has exactly one primary home. Islands either live in
  a packed canvas region OR a sidebar list — not duplicated across both.

## Sources

- Williams College CS326, *Graph Layout Algorithms* — "maximize distance between
  unconnected nodes" heuristic [L4]:
  https://www.cs.williams.edu/~freund/cs326/GraphLayout.html
- Freivalds, Dogrusoz, Kikusts, *Disconnected Graph Layout and the Polyomino Packing
  Approach*, Graph Drawing (GD 2001), LNCS 2265, pp. 378–391 [L4]:
  https://link.springer.com/chapter/10.1007/3-540-45848-4_30
- SO — *NetworkX draw places nodes awkwardly with disconnected nodes* (layout each
  component, then arrange) [L6]:
  https://stackoverflow.com/questions/71979236/networkx-draw-function-places-nodes-awkwardly-when-there-are-disconnected-node
- SO — *Graph layout disconnected subgraphs* (separate, non-overlapping components)
  [L6]: https://stackoverflow.com/questions/78740411/graph-layout-disconnected-subgraphs
- SO — *cose-bilkent disconnected nodes drift to corner* [L6]:
  https://stackoverflow.com/questions/56325879/how-to-control-the-position-of-disconnected-nodes-with-cose-bilkent-layout
- SO — *dagre with multiple trees / independent nodes shrinks everything* [L6]:
  https://stackoverflow.com/questions/32041577/how-to-deal-with-multiple-trees-situation-when-using-dagre-layout-in-cytoscape-j
- SO — *React Flow + dagre overlapping / custom layout* [L6]:
  https://stackoverflow.com/questions/79359437/react-flow-dagre-how-to-disable-overlapping
- Graphviz forum — *align loose nodes beside the main graph* (`packmode` array) [L4]:
  https://forum.graphviz.org/t/how-to-align-loose-nodes-beside-the-main-graph/429
- cytoscape.js-layout-utilities README — placing disconnected nodes with offset [L4]:
  https://github.com/iVis-at-Bilkent/cytoscape.js-layout-utilities/blob/master/README.md
