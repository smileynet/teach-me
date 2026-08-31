# Research — Accessibility of viz types + Desktop-first layout patterns (spike #275)

## Summary

For a **small, shallow navigation forest** (~9 nodes, depth 0–1, mostly parent/child + a few cross-links), the accessibility evidence points hard in one direction: **hierarchical/list-shaped viz types have a native, first-class accessible representation; free-form node-link graphs do not.** A tree/outline maps 1:1 onto the WAI-ARIA `tree` pattern (`role=tree` / `treeitem` / `group`, arrow-key navigation, `aria-expanded`) — screen readers understand it out of the box [L4:established]. An SVG node-link/DAG diagram (dagre) has **no matching ARIA role for arbitrary graphs**; the standing expert advice is to hide the SVG from AT and provide a **parallel text/list/table fallback** [L5/L6:established]. The project already ships a card-grid LIST view — that list *is* the accessible representation, so the honest architecture is: **the list view is the a11y-complete surface; the map is an enhanced, sighted-user visualization pointing at the same data.**

On layout, the desktop-first reframe is well-supported. The dominant scannable desktop pattern for "how do these things connect + drill in" is **master–detail** (grouped/columned index on the left, detail on selection) and **multi-column grouped sections** that fill horizontal space without horizontal scrolling. Vertical scanning beats horizontal scanning on desktop; horizontal space is best spent on **columns/sections side-by-side**, not on a wide scroll region [L6:reported]. The responsive-viz literature says desktop→mobile should **transform** (re-layout, re-encode, or swap to a simpler view), not just shrink — and swapping a graph for a list/accordion on narrow screens is an accepted, graceful degradation [L4:established].

---

## (A) Accessibility per visualization type

Ranked by how cleanly each maps to an existing accessible representation.

### 1. Indented tree / outline — **native ARIA support (best)**
- Maps directly to the **WAI-ARIA Tree View pattern**: container `role="tree"`, each node `role="treeitem"`, children wrapped in `role="group"`, parents carry `aria-expanded` (true/false; end nodes omit it) [L4:verified — W3C APG].
- Full keyboard model is specified: Up/Down move focus, Right opens/descends, Left closes/ascends, Home/End jump, type-ahead recommended for >7 root nodes, Enter activates (for a nav tree, activation = navigate to the page) [L4:verified].
- `aria-level`, `aria-posinset`, `aria-setsize` can be auto-computed from DOM structure (or declared) so AT announces "item 2 of 5, level 2" [L4:verified].
- The APG ships a dedicated **Navigation Treeview example** — exactly our use case (tree that links to a set of web pages) [L4:verified].
- **Verdict:** zero custom a11y engineering; the DOM *is* the accessible artifact. No parallel fallback needed.

### 2. HTML nested list / accordion — **native support, simplest**
- A `<ul>`/`<li>` nested list is inherently traversable; an accordion (disclosure buttons) is a well-trodden pattern. Léonie Watson's technique represents an SVG flowchart *as* nested lists using ARIA list semantics, precisely because lists are natively accessible [L5:reported — tink.uk via JointJS].
- **Verdict:** the card-grid LIST view the project already has qualifies here. It is the accessible baseline.

### 3. Sectioned columns / card-grid with drawn connectors — **accessible IF the DOM is list/region-shaped**
- If cards are real DOM elements grouped under headings (`<section>` + heading per group, cards as links), the reading/tab order is natural and accessible; the **connector SVG is decorative** and should be `aria-hidden="true"` [L4:established — decorative SVG guidance].
- Connectors add meaning for sighted users only; the *relationship* meaning must ALSO be conveyed in text (e.g. "Prerequisite: X" on the card) so it isn't color/line-only [L4:WCAG 1.4.1 use-of-color; L5 JointJS "don't rely on color alone"].
- **Verdict:** accessible as a styled list. The graph-ness is a visual enhancement layered over an accessible list.

### 4. SVG node-link diagram / DAG (dagre, force-directed) — **NO native role; needs a parallel fallback**
- **There is no ARIA role for an arbitrary node-link graph.** The ARIA Graphics Module only defines `graphics-document`, `graphics-object`, `graphics-symbol` — enough to *name parts* of a chart, not to convey graph topology/traversal [L4:established — W3C Graphics-ARIA].
- Expert consensus (Léonie Watson, screen-reader user Ryan Schugart): for complex SVGs/graphs, **the scalable techniques run out** — line charts → table, flowcharts → nested list work, but "as soon as you run into other complex visualizations, the ARIA semantics you need are lacking, so alternative routes … [provide] a secondary view with DOM elements alongside the graphical view" [L5:established — JointJS/tink.uk].
- Common, blunt recommendation: **hide the SVG from AT and provide the data in a table/list** ("Often your best option for complex SVGs, graphs etc. is to hide the SVG itself from screen readers and provide the data in a table") [L6:reported — Stack Overflow, but echoes expert view].
- Keyboard is also hard: focus must be managed manually (`tabindex="0"`/`-1`), positive `tabindex` is an anti-pattern, and SVG has no z-index so paint order fights focus order [L5:reported — JointJS].
- **Verdict:** the *most expensive* to make accessible and never fully native. Only justified if the graph view earns its keep for sighted users — and even then it MUST be backed by a parallel accessible list/table (which we already have).

### 5. Treemap / sunburst / radial — **poor for both a11y and comprehension here**
- NN/g: treemaps are "a complex, area-based data visualization … that can be hard to interpret precisely. In many cases, simpler visualizations such as bar charts are preferable" [L4:reported — NN/g]. Area-encoding of a 9-node nav forest adds cognitive load with no payoff.
- Same a11y problem as #4 (custom SVG, no native role) plus worse for low-vision (relies on area/angle).
- **Verdict:** wrong tool for a small navigation surface. Skip.

### Cross-cutting SVG a11y requirements (any SVG that stays visible)
- `role="img"` + first-child `<title>` + `<desc>`, linked via `aria-labelledby`; browsers surface `<title>` as a tooltip [L4:established — MDN/SVG2, Unimelb, ada-compliance]. (The project already has an SVG a11y pattern per steering.)
- **"No ARIA is better than bad ARIA"** — WebAIM Million found pages *with* ARIA averaged **34.2% more** detected errors; don't bolt fake graph semantics onto an SVG [L4:verified — WebAIM Million via JointJS].
- Never rely on color/line alone; label relationships in text [L4:WCAG 1.4.1].
- Respect `prefers-reduced-motion` for any animated layout/transition [L4:established — MDN].

### A11y bottom line
| Viz type | Native accessible representation? | Fallback needed? |
|----------|-----------------------------------|------------------|
| Indented tree / outline | Yes — ARIA `tree` pattern | No |
| Nested list / accordion | Yes — inherent HTML | No |
| Card-grid + decorative connectors | Yes, if DOM is list/region-shaped; connectors `aria-hidden` | No (relationship text on card) |
| SVG node-link graph / DAG (dagre) | **No** ARIA role for arbitrary graphs | **Yes — parallel list/table (mandatory)** |
| Treemap / sunburst / radial | No | Yes; also poor comprehension |

**Recommendation for #275:** treat the **card-grid LIST view as the accessibility-complete surface** (it already exists). Whatever map/relationship view is chosen should either (a) be a **tree/outline** (native a11y, cheapest) or (b) be an SVG graph that is `aria-hidden` and explicitly backed by that list. A tree/outline collapses the a11y problem entirely — no parallel artifact to keep in sync.

---

## (B) Desktop-first layout patterns (horizontal space) + mobile fallback

### Core principle: vertical scanning wins; spend horizontal space on side-by-side columns, not wide scroll
- Users scan desktop content **vertically**; horizontal scrolling "does not come naturally" and hurts scannability. Practitioners specifically prefer NOT to force horizontal layouts on desktop [L6:reported — UX StackExchange]. → Use the horizontal room for **parallel columns/panels**, not a horizontally-scrolling canvas (this directly indicts the current fixed-px, wide dagre canvas).
- For chart-heavy dashboards, place primary content along the **Z-scan path** (top-left → top-right → down) [L6:reported — kindatechnical].

### Pattern 1 — Master–detail (strongest fit for "connect + drill in")
- Grouped/columned **index on the left**, **detail panel on the right** that updates on selection. On tablet/desktop this is the canonical multi-column layout; it collapses to list-then-detail (drill-down) on mobile [L5:reported — lobehub Flutter master-detail; L6 UX SE].
- Caveat from practitioners: master–detail is great for browse+inspect but don't overload the master with columns ("more than ~7 columns you're doing it wrong") [L6:reported — UX SE]. For us the master is a grouped list of domain cards — well within bounds.
- **Fit:** landing page = master list of domains (grouped), selecting a domain shows its sub-map/summary in a detail region; click-through goes to the per-topic map page. Uses horizontal space, stays scannable, degrades to a single column on mobile.

### Pattern 2 — Multi-column grouped sections (best for the overview/landing)
- Break the forest into **groups as columns/sections** (e.g. one column per top-level domain cluster; islands become their own labeled section). Each section is a heading + a small stack of cards. This fills a wide viewport with **N columns of grouped cards**, reads top-to-bottom within each column, and reflows to fewer columns then one column as width shrinks (plain CSS grid `repeat(auto-fill, minmax(...))`).
- Avoids the dagre pain entirely: no rank-based horizontal fan-out, no fixed-px canvas, no "backward" edges; **CSS grid reflows for free** (the context file's stated pain points) [inferred from context file + L6 grid/scannability sources].
- Grids "ensure purposeful placement and alignment … visual rhythm and hierarchy" and are the standard blueprint for scannable desktop layouts [L6:reported — Medium grid guide].

### Pattern 3 — Horizontal tree / indented outline (best if relationships must be explicit)
- A left-to-right or indented tree reads naturally, scales to 30 nodes by scrolling vertically (indented) rather than fanning horizontally, and — critically — **is the ARIA `tree` pattern** so it's the a11y win from §A too. roadmap.sh popularized the "map of topics you could learn" as an interactive node graph, and is widely loved as an overview ("a terrific map … helps you understand where in the learning journey you are") but its dense graph is also the part people redraw/simplify [L6:reported — roadmap.sh; substack/medium "I revamped the Roadmap.sh Frontend Roadmap"]. Lesson: the *value* is the ordered overview, not the graph rendering per se.

### Prior art (how real products present a "map of topics")
- **roadmap.sh** — hand-authored node graph, click nodes to read topic detail. Beloved as an overview; the graph itself is frequently criticized as dense/hard to follow and gets community redesigns [L6:reported].
- **Duolingo path / Khan / Brilliant** — increasingly a **linear/branching path (a spine)**, not a free graph — easier to scan and to show progress. Supports the "shallow, ordered" framing over a full DAG.
- **Obsidian/Roam graph view** — force-directed graph is praised as *exploratory eye-candy* but repeatedly criticized as **not a practical navigation tool** (hairball at scale). Reinforces: force-directed is wrong for a navigation surface.
- **NN/g on treemaps** — hierarchical area viz is hard to read precisely; prefer simpler forms [L4:reported].

### Is a full DAG (dagre/Sugiyama) overkill here? — Yes, for navigation
- Sugiyama rank layout is built for **large directed graphs where layered ordering carries meaning** (dependency analysis). For ~9 shallow nodes that are *mostly a tree* with a few cross-links, it over-serves: it fans siblings wide, needs a fixed-px canvas, distorts around disconnected islands, and produces "backward"-pointing edges (all four are the context file's documented pains). A **CSS-grid/flow layout with a few drawn connectors**, or a **tree/outline**, is simpler to build, reflows natively, and is more accessible [inferred from context + L6 scannability/grid sources; L4 tree pattern].

### Mobile fallback (graceful degradation)
- Responsive-viz research: desktop→mobile should **transform** (re-layout, re-encode, or **swap to a simpler view**), not merely rescale — a graph that's legible on desktop is unreadable shrunk to a phone [L4:established — arXiv 2104.07724 "Design Patterns and Trade-Offs in Responsive Visualization"; Adobe Research; UW IDL CHI 2020].
- Concrete degradation ladder for our forest:
  1. **Desktop (wide):** multi-column grouped sections OR master–detail OR tree — full horizontal use.
  2. **Tablet (medium):** grid reflows to 2 columns; master–detail collapses detail below list.
  3. **Mobile (narrow):** single-column **list/accordion** (the LIST view). The relationship/map view is either hidden or replaced by the list — this is the accepted swap-to-simpler-view strategy and *also* the a11y-complete surface, so **the mobile fallback and the accessibility fallback are the same artifact** [L4:established responsive-viz; L5/L6 a11y].
- Because the LIST view already exists and is accessible, the fallback is **free** — no separate mobile build.

### Desktop-space bottom line
- Prefer **master–detail** (browse + inspect) or **multi-column grouped sections** (pure overview) over a wide graph canvas; use horizontal room for parallel columns, keep scanning vertical.
- Consider a **tree/outline** for the relationship view — it doubles as the native-accessible representation and scrolls (not fans) as it grows to 30.
- **Retire full-DAG dagre** for this navigation surface; it's built for analysis of large layered graphs, not a shallow nav forest.
- Mobile = the existing single-column list = also the a11y fallback. One artifact, three jobs.

---

## Sources (with URLs)

**(A) Accessibility**
- [L4:verified] WAI-ARIA APG — Tree View Pattern (roles, keyboard, aria-expanded/level/posinset; Navigation Treeview example): https://www.w3.org/WAI/ARIA/apg/patterns/treeview/
- [L4:verified] APG Navigation Treeview example: https://www.w3.org/TR/2021/NOTE-wai-aria-practices-1.2-20211129/examples/treeview/treeview-navigation.html
- [L4:established] W3C ARIA Graphics Module (graphics-document/object/symbol — no arbitrary-graph role): https://www.w3.org/TR/graphics-aria-1.0/
- [L5:established] JointJS — "How to Make Diagrams More Accessible" (SVG vs Canvas, live regions, alt text, secondary DOM view, tabindex, WebAIM Million ARIA stat): https://www.jointjs.com/blog/diagram-accessibility
- [L5:reported] Léonie Watson — accessible SVG flowcharts as nested lists: https://tink.uk/accessible-svg-flowcharts/ ; line graphs as tables: https://tink.uk/accessible-svg-line-graphs/
- [L6:reported] Stack Overflow — "hide the SVG from AT, provide data in a table" for complex SVGs: https://stackoverflow.com/questions/70373906/accessible-diagram-in-svg
- [L4:established] MDN / SVG2 title & desc, aria-labelledby (via a11y guides): https://www.unimelb.edu.au/accessibility/techniques/accessible-svgs ; https://www.adacompliancepros.com/wcag-guides/svg-img-role-text-alternative
- [L4:verified] WebAIM Million (ARIA-present pages averaged 34.2% more errors; contrast top failure): https://webaim.org/projects/million/
- [L4:reported] NN/g — Treemaps are hard to interpret; prefer simpler viz: https://www.nngroup.com/articles/treemaps/

**(B) Desktop-first layout + responsive fallback**
- [L4:established] "Design Patterns and Trade-Offs in Responsive Visualization for Communication" (desktop→mobile transform, not rescale): https://arxiv.org/html/2104.07724v1
- [L4:established] UW Interactive Data Lab — "Techniques for Flexible Responsive Visualization Design" (CHI 2020): http://idl.cs.washington.edu/files/2020-ResponsiveVis-CHI.pdf
- [L4:established] Adobe Research — Designing Responsive Visualizations: https://research.adobe.com/news/designing-responsive-visualizations/
- [L6:reported] UX StackExchange — vertical scanning preferred, horizontal scrolling unnatural on desktop: https://ux.stackexchange.com/questions/122210/ux-solution-for-dashboard-with-scrollable-content-boxes
- [L6:reported] UX StackExchange — Master/Detail approach & "~7 columns you're doing it wrong": https://ux.stackexchange.com/questions/45461/is-master-detail-design-the-best-approach-for-our-application
- [L5:reported] lobehub — Flutter master-detail (multi-column on desktop, drill-down on mobile): https://lobehub.com/skills/rodydavis-skills-snippets_flutter-master-detail-view
- [L6:reported] kindatechnical — Dashboard Layout Best Practices (Z-scan path): https://kindatechnical.com/data-visualization/dashboard-layout-best-practices-and-design-patterns.html
- [L6:reported] Medium — grid as blueprint for scannable layout/hierarchy: https://medium.com/@selvarajdeepak858/mastering-the-grid-a-designers-guide-to-structure-and-harmony-in-ui-ux-c68db26715d4
- [L6:reported] roadmap.sh (topic-map prior art) + community redesign critique: https://roadmap.sh/get-started ; https://medium.com/@saidur48/i-revamped-the-roadmap-sh-frontend-roadmap-d5e63d630977

## Open questions / gaps
- No hard usability data comparing tree-outline vs card-grid-with-connectors *specifically* for tiny nav forests; recommendation leans on a11y cost + reflow simplicity, not a controlled study.
- Obsidian/Roam graph-view criticism is well-known in community discourse but I did not fetch a single authoritative citation this pass — treat as [L6:inferred] until a source is attached.
- Exact breakpoints for the degradation ladder are a design decision, not sourced.
