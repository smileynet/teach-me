# Spike #275 — Visualization TYPE for a small shallow domain forest (desktop-first navigation)

## Summary

For a **small, shallow forest** (~9 nodes → ~30, depth 0–1, parent/child + a few cross-links)
whose job is **navigation/overview** (not analysis), the research consistently favors
**explicit-hierarchy, low-degrees-of-freedom layouts** over space-filling or physics-based ones:

- **Node-link and indented-tree layouts beat treemaps** on navigation and hierarchy-comprehension
  tasks; treemap is repeatedly the *least preferred* and slowest for basic navigation
  [L4:established, arXiv 1908.01277; upv.es ACHI 2017].
- **Traditional / orthogonal (rectilinear) tree layouts significantly outperform radial/sunburst**
  for hierarchy tasks — radial looks appealing but hurts on read tasks [L4:established, Burch 2011].
- **Hierarchical network layouts reduce cognitive load and are preferred over force-directed**;
  force-directed pays off only for *large* networks where you want emergent clusters, and it
  introduces clutter, non-determinism, and "25% of time spent on manual layout fixes"
  [L4:established, DHQ 2022; PMC12306815; Cambridge Intelligence].
- A **full DAG/Sugiyama layout (dagre) is overkill** here: it's built to route many-edge layered
  DAGs and minimize crossings — value the current data (mostly a 1-deep tree + a few cross-links,
  3 islands) doesn't have. Its costs (fixed-px canvas, wide sibling fan-out, backward edges,
  island distortion) are exactly the pain listed in the context.
- **Prior art in learning platforms leans on hand-laid spatial paths and grouped cards**, not
  auto-layout graphs: roadmap.sh (6th most-starred repo on GitHub) uses an authored roadmap;
  Duolingo/Brilliant use a linear/branching *path*; docs sitemaps use grouped columns. Obsidian's
  force-directed graph is admired as ambient art but widely criticized as poor for *navigation*.

**Shortlist for this project:** (1) **Sectioned card grid with drawn connectors** (CSS grid groups
+ a thin SVG EdgeLayer for the few cross-links), (2) **Horizontal (left-to-right) tidy tree** for
the parent/child spine, with islands as their own row. Keep force-directed, treemap, and full
dagre off the table.

## Comparison table

Scored for THIS use (small shallow forest, desktop-first navigation, static Preact site).
Scale: ✅ strong · ⚠️ mixed · ❌ weak.

| Candidate | Scannability | Growth to ~30 nodes | Navigation clarity | Impl. cost (static Preact) | Verdict |
|---|---|---|---|---|---|
| **Sectioned column / card-grid + connectors** | ✅ Reading-order rows/columns; groups act as labels | ✅ Reflows to new rows; CSS grid handles 30 easily | ✅ Card = destination; connectors show the few links | ✅ Low — CSS grid + small SVG overlay; no layout lib | **Recommend (primary)** |
| **Horizontal tidy tree (rectilinear, LTR)** | ✅ Explicit parent→child, left-to-right uses desktop width | ✅ Good to ~30 at depth 0–1; deep+wide needs scroll | ✅ Clearest hierarchy read [Burch 2011] | ✅ d3-hierarchy `tree()` layout or hand math; no dagre | **Recommend (alt)** |
| **Indented / outline tree** | ✅ Familiar, novice-friendly [uvic 2013] | ⚠️ Breadth & depth contend for space; lots of scrolling [Stanford/UW] | ✅ For pure trees; ⚠️ cross-links awkward | ✅ Nested `<ul>`; trivial, a11y-native | Good LIST fallback; weak for cross-links |
| **Radial tree / sunburst** | ⚠️ Center-out; labels rotate, hard to read | ⚠️ Angular crowding as nodes grow | ⚠️ Sunburst conveys structure but underperforms rectilinear on tasks [Burch 2011] | ⚠️ Medium — polar math, label rotation | Not recommended |
| **Treemap** | ❌ Nesting implies hierarchy weakly | ⚠️ Fine for many leaves but not few large nodes | ❌ Least preferred; slowest basic navigation [arXiv 1908.01277] | ⚠️ Medium — squarify algo | Not recommended |
| **Force-directed** | ❌ Non-deterministic, clutter/overlap [arXiv 1712.05548] | ❌ Overkill for <30; built for large-network cluster discovery | ❌ Positions carry no stable meaning; poor for wayfinding | ❌ High — sim loop, tuning, "25% manual fixup" [PMC12306815] | Not recommended |
| **Subway / railway map** | ✅ Very legible IF paths are linear | ❌ Only shines for sequential paths; our forest is branchy w/ islands | ✅ Strong metaphor for a *journey* | ❌ High — hand-authored line routing | Not recommended (wrong shape) |
| **Full DAG / dagre (current)** | ⚠️ Wide sibling fan-out | ❌ Fixed-px canvas doesn't reflow; islands distort | ⚠️ Backward edges from shared child + cross-links | ⚠️ Have it, but fights the data | Replace |

## Recommendation

**Primary: sectioned card-grid with a thin connector overlay.**
- Lay domain cards in a responsive **CSS grid**, grouped into labelled sections (roots and their
  sub-maps together; islands in their own "Standalone" section). The section headings do the
  hierarchy work that a tree's edges would — cheaply and accessibly.
- Draw only the **few `leads_to` cross-links** as an SVG `EdgeLayer` on top (the existing
  component), not every parent/child edge. Parent/child is implied by grouping, so you avoid the
  backward-edge and fan-out problems entirely.
- This uses desktop horizontal space well (multi-column), **reflows** for mobile (columns collapse
  to one — graceful degradation), and keeps the card = navigation target. It matches how
  docs sitemaps and course catalogs present "how subjects connect."

**Alternative when the parent/child spine matters more than grouping: horizontal tidy tree.**
- Rectilinear, left-to-right (`d3-hierarchy.tree()` gives positions; render with the existing
  Preact cards + SVG connectors — no dagre). LTR exploits desktop width and gives the clearest
  hierarchy read per Burch 2011. Islands become sibling roots in an extra row.

**Explicitly reject:** treemap (worst for navigation), force-directed (overkill/unstable for <30
nodes), radial/sunburst (underperforms rectilinear on read tasks), full dagre DAG (solves a
crossing-minimization problem this data doesn't have).

**Accessibility / mobile:** both recommended types degrade to a **single-column ordered list**
(the LIST view the project already has as the low-cognitive-load default). Keep color-not-alone
(section labels + text badges, not just edge color), `role="img"`+`<title>` on the SVG overlay per
the project's a11y pattern. The card-grid is DOM-native and screen-reader friendly by default; the
tree needs an equivalent nested-list fallback.

**On the dagre question (#2 in context):** yes, a full DAG layout is overkill. Sugiyama/dagre earns
its complexity when you have many edges across many ranks and crossing-minimization is the point.
Here the graph is essentially a 1-deep tree plus a handful of cross-links and disconnected islands —
a CSS-grid/flow layout with drawn connectors (or a plain tidy-tree) is simpler, reflows, and reads
better for navigation.

## Sources (with URLs)

- [L4:established] Interactive Visualisation of Hierarchical Quantitative Data (arXiv 1908.01277) — "Treemap was the least preferred and had slower performance on a basic navigation task and slower performance and accuracy in hierarchy understanding tasks." https://arxiv.org/html/1908.01277v3
- [L4:established] Burch et al., *Evaluation of Tree Layouts* (2011) — "traditional and orthogonal tree layouts significantly outperform radial tree layouts for the given task." https://joules.de/files/burch_evaluation_2011.pdf
- [L4:established] Node-link vs Treemap vs Icicle eye-tracking study (ACHI 2017) — nodelink and icicle perform well; treemap only exceeds chance on one easy task. http://personales.upv.es/thinkmind/dl/conferences/achi/achi_2017/achi_2017_4_30_28003.pdf
- [L4:established] Fu et al., *Indented Tree or Graph? A Usability Study of Ontology Visualization* (ISWC 2013) — indented tree more organized/familiar to novices; graph more controllable for multiple inheritance. https://chisel.cs.uvic.ca/pubs/fu-ISWC2013.pdf
- [L4:reported] Stark et al., *Space-Filling Visualizations for Hierarchies* (Sunburst vs Treemap) — Sunburst favored for conveying structure; treemap has higher learning cost. https://www.cs.kent.edu/~jmaletic/cs63903/papers/stask00.pdf
- [L4:established] *Perceptual Effects of Hierarchy in ... Social Networks* (DHQ 2022) — "hierarchical network representations reduce cognitive load and lead to more frequent and deeper insights ... users report a preference for the hierarchical graph representation" (over force-directed). http://www.digitalhumanities.org/dhq/vol/16/1/000604/000604.html
- [L4:established] *User-Guided Force-Directed Graph Layout* (PMC12306815) — poor layouts cost users "up to 25 percent of their time on manual layout adjustments." https://pmc.ncbi.nlm.nih.gov/articles/PMC12306815/
- [L4:reported] *Persistent Homology Guided Force-Directed Graph Layouts* (arXiv 1712.05548) — force-directed "clutter and overlap of unrelated structures can lead to confusing graph visualizations." https://arxiv.org/html/1712.05548v4
- [L4:reference] Stanford CS448B / UW CSE512 lecture notes — indentation trees: "breadth and depth contend for space ... often requires a great deal of scrolling"; tree layout is O(n)/O(n log n), interactive. https://hci.stanford.edu/courses/cs448b/f09/lectures/CS448B-20091021-GraphsAndTrees.pdf · https://courses.cs.washington.edu/courses/cse512/25sp/lectures/CSE512-Networks.pdf
- [L5:reference] roadmap.sh (prior art) — community-curated, hand-authored spatial roadmaps for topic navigation; 6th most-starred GitHub project. https://roadmap.sh/about
- [L4:reference] Microsoft 365 blog — "Treemaps ... better suited for comparison among hierarchical levels ... rectangles and straight lines are easier to compare than slices and angles." https://www.microsoft.com/en-us/microsoft-365/blog/2015/08/11/breaking-down-hierarchical-data-with-treemap-and-sunburst-charts/
