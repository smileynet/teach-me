# Prior Art — How Real Products Present a "Map of Topics / Domains / Courses"

Research for spike #275 (reconsider the forest/map visualization type, desktop-first).
Question 4 of the context: what works, what's criticized, for topic/domain overview surfaces.

## Summary

The strongest signal across every product studied: **force-directed / free-floating graph
views are consistently praised as beautiful and consistently criticized as useless for
navigation.** The pattern that keeps winning for *navigation* is a **structured, stable,
directional layout** — a curated tree, a linear/branching path, or an indented outline —
NOT an auto-laid-out node cloud.

Concrete industry moves that matter for #275:

- **Duolingo** deliberately *replaced* its explorable "tree" (many routes, unpredictable) with a
  single guided **"path"** — a stable, linear, winding trail. Cited reason: the tree let two
  learners "end up in different places"; the path gives one predictable, scannable route.
  [L4:established]
- **Khan Academy** *retired* its famous graph-style **Knowledge Map** (a Google-Maps-style
  pannable web of concept nodes). Cited reasons: it "did not pair well" with new subjects, the
  code was unmaintainable, and **"most students and teachers found that the linear course
  progression works best."** [L4:established]
- **roadmap.sh** — the single most successful "topic map" on the web (6th–7th most-starred repo
  on GitHub, hundreds of thousands of monthly visitors) — uses a **hand-authored, directional
  flowchart with clickable nodes**, NOT an auto-layout graph. Curation and stable position are
  the product. [L4:established]
- **Obsidian graph view** is the canonical cautionary tale: users repeatedly call it a "visual
  toy," "abstract painting," "non-functional for navigation" because **node positions change on
  every load** and it gets "crowded and unreadable" past a few dozen nodes. [L5:established]

**Takeaway for our forest (~9→30 nodes, navigation surface, desktop-first):** emulate the
roadmap.sh / indented-tree / stable-directional model. Avoid the force-directed graph and avoid
fixed-pixel auto-layout that reflows unpredictably. If we keep a "map," it must have **stable,
authored-feeling positions and a clear reading direction**, with edges as reinforcement — not as
the primary way to find a node.

---

## Per-Product Notes

### 1. roadmap.sh — hand-authored directional flowchart (EMULATE)
- **Layout:** A vertical, top-to-bottom **flowchart / dependency chart**. Nodes are topic boxes;
  a clear "spine" runs down the middle with branches off to the sides. Positions are
  **hand-authored**, not algorithmically laid out. Two roadmap kinds: *role-based* (Frontend,
  DevOps) and *skill-based*. [L4:verified — roadmap.sh/about]
- **Interaction:** "Roadmaps are now interactive — you can click the nodes to read more about the
  topics" and get curated resources; progress can be tracked per node.
  [L4:verified — developer-roadmap README]
- **PRAISED:** Clear next-step guidance for "confused" learners; the stable authored layout means
  the same node is always in the same place; scannable spine; curated (SME-reviewed) so the map
  itself is the value, not raw links. Built as a **static site (Astro + Tailwind on GitHub
  Pages)** — directly relevant to our static-site constraint. [L4:verified]
- **CRITICIZED:** Can be dense/overwhelming for a single big role roadmap; but this is mitigated
  by the authored spine (you always know where to start).
- **Why it works:** direction + curation + stable position. It's a *map you read*, not a graph
  you untangle.
- Sources: https://roadmap.sh/about · https://roadmap.sh/get-started ·
  https://github.com/kamranahmedse/developer-roadmap/blob/master/readme.md

### 2. Duolingo — the "tree → path" reboot (EMULATE the reasoning)
- **Old:** "the tree" — a main screen that "let people explore numerous routes." Explorable,
  branching, learner-chosen order.
- **New (2022):** "the path" — a **single winding linear trail** of lesson bubbles. All users
  follow one route.
- **PRAISED:** Predictability and momentum. Apple's design writeup quotes VP of design Ryan Sims:
  with the tree, "Two people could spend the same number of hours doing the same number of
  lessons, but end up in different places." The path fixes that. CNET: "the winding path design
  also adds a confidence boost when you scroll back up through completed lessons… the path-like
  style makes completing lessons feel more like a journey." [L4:established]
- **CRITICIZED:** Loss of learner agency (can't jump around freely) — a deliberate trade-off they
  accepted in favor of guidance and clarity.
- **Relevance to us:** Confirms that for *navigation/motivation*, a **stable, directional,
  scannable path beats a free-explore branching structure.** Our forest is an overview (not a
  forced sequence), but the "one obvious reading order + stable positions" lesson transfers.
- Sources: https://developer.apple.com/news/?id=jhkvppla ·
  https://blog.duolingo.com/new-duolingo-home-screen-design/ ·
  https://www.cnet.com/tech/services-and-software/8-changes-duolingo-made-for-easier-language-learning-in-2022/

### 3. Khan Academy — the Knowledge Map, RETIRED (AVOID / cautionary)
- **What it was:** A Google-Maps-style **pannable, zoomable web of math concept nodes** with
  dependency links — a literal topic graph. It was a signature, celebrated feature.
- **Why retired:** Official Help Center: "This feature was removed… replaced with the Missions
  System (now Course Mastery). The Knowledge Map **did not pair well with the other subjects** we
  expanded into, and the **code was no longer maintainable.**" A separate official reply:
  **"Most students and teachers have found that the linear course progression works best for
  them,"** while acknowledging a dependency tree "could be helpful in some instances."
  [L4:established]
- **PRAISED (by nostalgic users):** "one of the standout features that put KA on the map";
  users still petition to bring it back — so the *visual appeal* was real.
- **CRITICIZED / failure modes:** didn't scale across subjects; high maintenance cost; the
  linear progression served most users better for actually *doing the work*.
- **Relevance to us:** A beloved graph map can still be the wrong primary navigation. Scaling
  (their subject growth ≈ our 9→30 domains) and maintenance were the killers. Our forest should
  not become an unmaintainable bespoke graph.
- Sources: https://support.khanacademy.org/hc/en-us/community/posts/360077567752-Visual-Web-of-Math-Concepts ·
  https://support.khanacademy.org/hc/hy/community/posts/360027982751-What-happened-to-the-knowledge-map ·
  https://support.khanacademy.org/hc/en-us/community/posts/115007007148-Bring-back-the-Knowledge-Map

### 4. Brilliant.org — "Learning Paths" = ordered course lists (EMULATE lightweight)
- **Layout:** "Learning Paths are guided sequences of courses… Each path organizes related
  courses in a **logical order** so you learn progressively — starting with core ideas and
  building toward more advanced topics." Presentation is essentially an **ordered, sectioned
  list / stepped sequence**, not a graph. Heavy on gamified motivation (streaks, levels, daily
  goals) and Rive animations. [L4:verified — brilliant.org/help]
- **PRAISED:** Clear progression; low cognitive load; the *sequence* is the navigation.
  Third-party design reviews praise the playful, motivating flow (ustwo case study, Rive blog).
- **CRITICIZED:** More about content pacing than structure; the structure itself is
  uncontroversial precisely *because* it's a simple ordered list.
- **Relevance to us:** Reinforces that a **sectioned/ordered list is a legitimate, low-risk
  primary navigation** — which matches the context's "LIST view (card grid) is the
  low-cognitive-load default." Brilliant essentially ships only the list.
- Sources: https://brilliant.org/help/features/what-are-learning-paths/ ·
  https://ustwo.com/work/brilliant/ · https://rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations

### 5. Obsidian graph view — the "visual toy" (AVOID for navigation)
- **Layout:** Force-directed node cloud (global + local). Auto-positioned, physics-simulated.
- **CRITICIZED (heavily, in Obsidian's own forums):**
  - "the graph currently serves more as a **visual toy** than a truly powerful organizational
    tool." [L5:reported]
  - "whenever a graph view makes it to the starboard channel, it is always because it shows a
    nice pattern, **a bit like an abstract painting.**" [L5:reported]
  - **Instability is the #1 navigation killer:** "You can not use the default global graph to
    'view' notes because **the position of each note changes on every load.** The graph also
    becomes crowded and unreadable due to overlapping nodes. This problem even occurs at depth=2
    on the local graph." [L5:reported]
  - "Everytime you click on different nodes… it re-renders & re-arranges the nodes on each click.
    I find this re-arrangement **disorienting.** It makes it extremely difficult to use GraphView
    as a navigate tool." → drove the request to *pin/lock* the graph. [L5:reported]
  - Global graph "is also effectively useless… without the options to tweak settings."
    [L5:reported]
- **PRAISED (the narrow win):** The **LOCAL** graph — "which notes the current note links to" —
  is "far more meaningful" than the global blob. i.e., graph is useful as a *scoped, contextual*
  neighbor view, not a global overview. [L5:reported] Third-party fix (XDA): a plugin that
  clusters/tames it makes it "actually useful" — implying the default is not.
- **Relevance to us (biggest single lesson):** This is exactly the risk in our current
  dagre/fixed-px approach — "islands distort/waste space," edges point "backward," layout
  doesn't reflow. The failure mode Obsidian users describe (unstable positions, crowding,
  disorientation) is precisely what to avoid. **Stable, deterministic positions are
  non-negotiable** for a navigation map.
- Sources: https://forum.obsidian.md/t/graph-update/101944 ·
  https://forum.obsidian.md/t/usage-of-graph-view/19692 ·
  https://forum.obsidian.md/t/whats-the-point-of-the-graph-view-how-are-you-using-it/71316/19 ·
  https://forum.obsidian.md/t/option-to-pin-local-graphview-to-lock-the-graph-prevent-it-from-re-rendering-the-map/57421 ·
  https://forum.obsidian.md/t/you-all-say-the-graph-is-useless-let-me-show-you-how-to-use-it/116738 ·
  https://www.xda-developers.com/obsidian-plugin-makes-graph-feature-less-overwhelming-useful/

### 6. Skill-tree UIs (games / web components) — directional lattice (EMULATE selectively)
- **Layout:** A **directional lattice/DAG with authored positions** — nodes flow along a clear
  axis (top→down or left→right), prerequisite edges connect them, tiers are visually banded.
  Web components exist (Hkattelu/SkillTree — "dependency-free vanilla JS"; Beautiful Skill Tree —
  "visualize user progression in apps, games, training systems"). [L6:reported]
- **PRAISED:** Prereq relationships are legible; progression/locked-vs-unlocked state reads at a
  glance; strong motivational affordance (RPG familiarity).
- **CRITICIZED:** Can look busy; only works when someone *authors* the tier structure — an
  auto-layout skill tree loses the readability. Requires bounded node counts per tier.
- **Relevance to us:** The skill-tree pattern is a **stable, authored, directional DAG** — the
  "good" version of what dagre tries to be automatically. If we keep edges/DAG semantics, the
  lesson is: **band by tier, fix positions, keep direction consistent.** Our forest is shallow
  (depth 0–1) so a light tiered lattice or grouped columns is plausible.
- Sources: https://github.com/Hkattelu/SkillTree ·
  https://thelinuxcode.com/introducing-beautiful-skill-tree-v1-an-interactive-way-to-visualize-user-progression/

### 7. Documentation-site navigation / IA theory (EMULATE the default)
- **Dominant pattern:** **collapsible sidebar tree + breadcrumbs**, organized by user intent
  (frameworks like Diátaxis, task-based IA, topic-based authoring). Progressive disclosure via
  accordions, tabs, collapsible groups "reduces cognitive load by revealing content only when
  needed." Multi-product docs add a "product switcher." [L4:established — Fern IA guide]
- **NNG distinction (important framing):** an **information architecture** is the underlying
  structure; a **sitemap is a *visualization tool* used predominantly for planning** — i.e., the
  pretty node-graph is a *planning artifact*, not the end-user navigation surface. Breadcrumbs
  are the recommended lightweight "where am I" aid. [L4:established — NNGroup]
- **PRAISED:** Indented/collapsible trees scale to hundreds of pages, are keyboard-navigable,
  accessible, and degrade trivially to mobile.
- **CRITICIZED:** Deep nesting ("five layers of menus") buries content — keep hierarchy shallow.
- **Relevance to us:** For a *navigation* surface, the industry default is a **tree/outline +
  breadcrumbs**, and the graph is explicitly categorized as a *planning* visualization. Strong
  support for making the **list/outline the default** and treating the map as secondary.
- Sources: https://buildwithfern.com/post/information-architecture-best-practices-documentation ·
  https://www.nngroup.com/articles/information-architecture-sitemaps/ ·
  https://www.nngroup.com/articles/breadcrumbs/

---

## What to Emulate

1. **Stable, deterministic positions.** The single loudest cross-product lesson (Obsidian). A
   node must be in the same place every load. Never physics/re-layout on interaction.
2. **A clear reading direction / spine** (roadmap.sh flowchart, Duolingo path, skill tree). One
   obvious entry point and flow, not a symmetric blob.
3. **Curation over auto-layout.** roadmap.sh's authored positions and Khan's "linear works best"
   both say: a *designed* structure beats an algorithmic one for navigation.
4. **List/outline as the low-cognitive-load default; map as the secondary "relationship" view.**
   Matches the context's stated intent and the docs-IA + Brilliant evidence. NNG explicitly
   frames graph/sitemaps as planning tools, not primary navigation.
5. **Band/group by tier or domain group** to use desktop horizontal space while staying scannable
   (skill-tree tiers, roadmap.sh side-branches, doc sidebar groups). Sectioned columns > wide
   sibling fan-out.
6. **Progressive disclosure + breadcrumbs** for scale to 30 nodes (docs IA). Collapse islands /
   subgroups rather than letting them distort the whole canvas.
7. **Clickable nodes that lead somewhere** (roadmap.sh) — the node is a real navigation target,
   which we already do (node → domain map page).

## What to Avoid

1. **Force-directed / physics graph as the PRIMARY overview.** Universally praised as pretty,
   universally criticized as useless for navigation (Obsidian "visual toy" / "abstract
   painting"; Khan retired theirs). This is the "looks cool but useless" critique the spike asked
   about — confirmed repeatedly.
2. **Re-layout on load or on click.** Disorienting; the top Obsidian complaint. Our dagre canvas
   partially shares this risk (islands shift, edges point backward).
3. **Fixed-pixel canvas that doesn't reflow** — directly named as a current pain; conflicts with
   desktop-responsive + mobile-fallback goals.
4. **Wide symmetric sibling fan-out** (the current dagre pain). Rank-based layout spreads siblings
   horizontally with no reading priority — the opposite of a scannable spine.
5. **Deep nesting / many menu layers** (docs IA warning). Keep it shallow — our forest is depth
   0–1, so preserve that.
6. **Bespoke unmaintainable graph code.** Khan explicitly cited maintenance + poor scaling across
   growth as reasons to kill their map. Prefer a simple, stable layout we can maintain as domains
   grow to 30+.

## Recommended direction for #275 (synthesis, not a decision)
For a small, shallow, growing (9→30) **navigation** forest on a **static desktop-first** site,
the evidence favors: **a stable, authored-feeling, directional layout** — an **indented/collapsible
tree or grouped/sectioned columns with drawn connectors** (CSS-grid/flow + SVG edges) — with the
**card grid/list as the default** and the map as a secondary relationship view. This drops the
Sugiyama/dagre auto-layout (overkill and the source of the reflow/fan-out/backward-edge pains) in
favor of deterministic positions. If a DAG feel is wanted, tier-band it like a skill tree with
fixed positions. Avoid force-directed graphs entirely for the primary surface.

---

## Sources (with URLs)

**roadmap.sh**
- https://roadmap.sh/about
- https://roadmap.sh/get-started
- https://github.com/kamranahmedse/developer-roadmap/blob/master/readme.md

**Duolingo**
- https://developer.apple.com/news/?id=jhkvppla (Behind the Design: Duolingo — "tree" → "path")
- https://blog.duolingo.com/new-duolingo-home-screen-design/
- https://www.cnet.com/tech/services-and-software/8-changes-duolingo-made-for-easier-language-learning-in-2022/

**Khan Academy (Knowledge Map retirement)**
- https://support.khanacademy.org/hc/en-us/community/posts/360077567752-Visual-Web-of-Math-Concepts
- https://support.khanacademy.org/hc/hy/community/posts/360027982751-What-happened-to-the-knowledge-map
- https://support.khanacademy.org/hc/en-us/community/posts/115007007148-Bring-back-the-Knowledge-Map

**Brilliant.org**
- https://brilliant.org/help/features/what-are-learning-paths/
- https://ustwo.com/work/brilliant/
- https://rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations

**Obsidian graph view critique**
- https://forum.obsidian.md/t/graph-update/101944 ("visual toy")
- https://forum.obsidian.md/t/usage-of-graph-view/19692 ("abstract painting")
- https://forum.obsidian.md/t/whats-the-point-of-the-graph-view-how-are-you-using-it/71316/19 (position changes every load, crowded at depth 2)
- https://forum.obsidian.md/t/option-to-pin-local-graphview-to-lock-the-graph-prevent-it-from-re-rendering-the-map/57421 (re-render disorienting)
- https://forum.obsidian.md/t/you-all-say-the-graph-is-useless-let-me-show-you-how-to-use-it/116738 (local graph is the narrow win)
- https://www.xda-developers.com/obsidian-plugin-makes-graph-feature-less-overwhelming-useful/

**Skill-tree UIs**
- https://github.com/Hkattelu/SkillTree
- https://thelinuxcode.com/introducing-beautiful-skill-tree-v1-an-interactive-way-to-visualize-user-progression/

**Documentation IA / navigation theory**
- https://buildwithfern.com/post/information-architecture-best-practices-documentation
- https://www.nngroup.com/articles/information-architecture-sitemaps/ (sitemap = planning viz, not primary nav)
- https://www.nngroup.com/articles/breadcrumbs/

## Open Questions
- Does our forest have a natural "spine" / entry domain to anchor a directional layout, or are
  domains genuinely peer-level (favoring grouped columns over a single path)?
- For the 3 disconnected islands: group them into a labeled "standalone" section (docs-IA style)
  rather than floating them in a graph canvas?
- Is an indented collapsible tree enough, or do the few `leads_to` cross-links justify keeping
  drawn connectors (skill-tree lattice) at all?
