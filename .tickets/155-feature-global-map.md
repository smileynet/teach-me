---
id: "155"
title: "Feature: global map — unified view of all domain maps with lazy cross-domain connections"
status: done
blocked_by: ["150", "152"]
priority: medium
type: feature
tags: [source-ingest, platform]
---

# Feature: global map

## Problem

Each domain gets its own MAP.md — but the learner's knowledge spans multiple domains. There's no unified view showing:
- What domains exist and their completion state
- How domains connect (shared concepts, prerequisite chains)
- What's an island (no connections to other domains) vs what's in a cluster

The existing `leads_to` field in MAP.md is hand-authored and rarely populated. Cross-domain connections should emerge from evidence, not be manufactured.

## Plan (research + review, 2026-08-29) — PHASED; Phase 1 folds in #260

Blockers #150/#152 are DONE → unblocked. Evidence:
`.scratch/review/map-render-surface.md`, `.scratch/review/crossmap-prereq-260.md`,
`.scratch/research/cross-domain-edges.md`, `.scratch/research/graph-of-graphs-viz.md`.

### Phase 1 (THIS ticket) — structural forest map + close #260
Structural edges only (higher precision than similarity — research: similarity asserts
relatedness not dependency, and similarity nets go near-complete on a small corpus;
explicit edges are the trusted seed). Build:
1. `tools/generate_global_map.py`: `find_maps` (reuse) → `load_map` each (reuse) → build
   load-once `by_domain` dict → synthesize DOMAIN-level edges from `.parent` (parent/child)
   and `.leads_to` (frontmatter list, navigational). Do NOT reuse the `depth>0 → None` skip
   (that guard is in generate_index_page.parse_map_meta, NOT find_maps) — keep children.
   Per-domain completion via `_overlay_status_map` + `status_map.get(t.id)` counting,
   OVERLAY-ONLY (match the index; the per-domain page's disk-derived compute_effective_status
   would diverge). Emit a domain-level `page-data` island; call `render_map_page` (reuse,
   component-agnostic) with a new module_script. `mise run map:global`.
2. New client `assets/components/GlobalMapView.js` + `DomainCard.js` (MapView/TopicCard are
   hard-wired to the topic model + ULID keys — NOT reusable). Lift generic `computeLayout` +
   `EdgeLayer` + `.dag-*` CSS. Viz (graph-of-graphs research): compound/meta-node model, do
   NOT mix sub-nodes+meta-nodes in one dagre pass; islands component-packed + sidebar (not
   forced into a row); node size=topic count, color=completion; click domain → its map page.
3. Close #260: add `build_forest_index(maps)` (union slug/alias→id, WITH duplicate-slug
   detection — ULID keys disambiguate) + `validate_forest(maps)` (union prereq check +
   forest-wide cycle check) to map_parser.py, and REWIRE the check-maps/verify gate to run
   validate_forest per domain-map-set. This is the same forest union #155 needs anyway. The
   4 cross-map prereqs (blender texture-audit/ramp-band-textures/wiring-the-shader,
   mktoon configurable-banding → toon-banding/configurable-banding in siblings) are
   INTENTIONAL forks (orientation prose confirms) → #260 decision = VALID (Option A).
4. Extract shared helpers (`_overlay_status_map`, `.dag-*` CSS) so index + per-domain +
   global map share one impl each.

### Phase 2 (separate ticket) — concept-based connection detection
YAKE shared-concept + first-mention prereq-bridge edges, as AUTHOR-CONFIRMED SUGGESTIONS
(never auto-committed — research: high false-positive risk on small corpus; surface
sub-threshold links as unverified). Needs cached `.concepts.json` + `cross_domain_edges.py`.

### Phase 3 (separate ticket) — lazy/triggered detection + auto-regen
Detect on domain completion / "where does this lead"; auto-regen policy.

### Out of scope (Phase 1)
Cross-map prereq EDGE SYNTHESIS for availability gating (functional change beyond validation
— review flagged; defer). Concept similarity. Confidence thresholds/weights.

### Answered open questions
- Replace or complement index? → COMPLEMENT (keep index flat dashboard; add global-map.html
  graph view; cross-link). Global map may become the default landing in a later ticket.
- Sibling forks inline on parent vs global map? → Phase 1 renders them in the global/forest
  view; inline-on-parent fork rendering is a nice-to-have deferred.

## What to build (original)

A **global map** that aggregates all domain MAPs into a single navigable graph with lazily-detected cross-domain edges.

### Core model

```
global-map.json (generated, cached)
├── domains: [{slug, title, topic_count, completion%, position}]
├── islands: [domain slugs with no cross-domain edges]
└── connections: [{from_domain, to_domain, type, evidence, weight}]
```

### Connection detection (lazy, on-demand)

Connections are NOT pre-computed for all pairs. They're detected when:
1. A new domain is generated → check if its concepts overlap with existing domains
2. A learner completes a domain → "where does this lead?" triggers connection search
3. Explicit `leads_to` fields in MAP.md → always included

**Detection mechanisms:**

| Type | How | Evidence |
|------|-----|----------|
| Shared concepts | YAKE concepts that appear in both domains' chunks | concept term + chunk references |
| Prereq bridge | Topic in domain B uses a term defined in domain A | first-mention edge crossing domains |
| leads_to (explicit) | MAP.md frontmatter | author declaration |
| Topic name overlap | Identical or near-identical topic slugs across maps | slug similarity + content cosine |

### Visualization

Generate an interactive HTML page (Preact + dagre, matching existing map page pattern):
- Each domain is a node (sized by topic count, colored by completion)
- Cross-domain edges shown as thin connectors with hover-to-explain
- Islands float disconnected (not forced into a layout)
- Click a domain → navigates to its domain map page

### "Topic islands" handling

Domains with zero detected connections to others are explicitly surfaced:
- Shown as islands in the visualization (spatially separated)
- Listed in a sidebar: "Standalone domains (no detected connections)"
- NOT treated as a problem — some domains are genuinely independent
- When new connections are detected later, islands naturally join the graph

## CLI

```bash
python tools/generate_global_map.py --scan-dir workspace/maps/ --output workspace/global-map.html
mise run map:global  # shorthand
```

## Architecture

```
workspace/maps/*.MAP.md
    │
    ▼ (map_parser.py — already works)
Per-domain DomainMap objects
    │
    ▼ (extract_concepts.py — per-domain, cached as .concepts.json)
Per-domain concept sets
    │
    ▼ (new: cross_domain_edges.py)
Connection detection: shared concepts + prereq bridges
    │
    ▼ (new: generate_global_map.py)
global-map.html (interactive Preact page)
```

## Acceptance criteria

### Phase 1 (THIS ticket — structural + #260)
- [x] `tools/generate_global_map.py` generates a forest map HTML from all MAP.md in a
      scan-dir (domains as nodes; parent/child + `leads_to` edges); `mise run map:global`
- [x] Domain nodes sized by topic count, colored by OVERLAY completion (matches index)
- [x] Surfaces topic islands without treating them as errors (sidebar + separate placement)
- [x] Clicking a domain navigates to its map page (href correct; cross-workspace resolution
      is #198's job)
- [x] Handles the `leads_to` frontmatter field as explicit edges
- [x] Works with 1 domain (single node), 5 domains, and 20+ domains (tested 1/5/22)
- [x] Visual matches existing map page style (dagre, same palette; new GlobalMapView/DomainCard)
- [x] **Closes #260:** `build_forest_index` + `validate_forest` in map_parser; forest gate
      (`check-maps-forest.py`) wired into verify; the 4 cross-map prereqs validate clean;
      `mise run verify` + `check-maps` EXIT 0

### Deferred (Phase 2/3 — separate tickets #266/#267)
### Deferred to follow-up tickets (NOT ACs of this ticket — moved out per the phase split)
- Detects shared-concept connections between domains → **#266** (Phase 2, author-confirmed)
- Lazy detection: only computes connections when triggered → **#267** (Phase 3)

## Concrete use case: sibling map fork (godot-toon-shaders ↔ godot-mktoon)

The godot-gamedev parent has two depth-1 child MAPs that share a prerequisite:

```
godot-gamedev (parent)
├── godot-toon-shaders (child)
│   └── toon-banding ← shared fork point
│       → outlines → advanced-outlines → color-simplification
│
├── godot-mktoon (child)
│   prereqs: [toon-banding] ← references topic in SIBLING map
│   → gooch → wrap → specular/rim → outlines-overlays → vfx
```

Both tracks branch from `toon-banding` (in the toon-shaders map). They teach different
philosophies for the same problem: post-process filtering vs per-material authored NPR.

**Requirements this case demands:**

1. The parent map page must render the fork visually — `toon-banding` node has two outgoing
   paths leading to different child maps, not just a single "zoom in" node per child.
2. Cross-map prereqs (`godot-mktoon` prereqs `toon-banding` from `godot-toon-shaders`) must
   resolve when building the global graph. This is an intra-parent sibling reference, not a
   cross-domain connection.
3. A learner on the parent map sees both paths as alternatives from the fork point, with a
   brief "Filter vs Author" decision label on the fork.

**This is the primary motivating case for "how to handle depth-1 child maps."**

## Open questions

- Should connections have a confidence threshold (don't show weak ones by default)?
- Should the global map auto-regenerate on domain completion, or only on explicit request?
- ~~How to handle depth-1 child maps (e.g., sub-topics that expand into their own MAP)?~~ → Answered above: render fork points where siblings share prereqs.
- Does this replace or complement the existing index page (generate_index_page.py)?
- Should sibling-map forks show inline on the parent map, or require navigating to the global map?

## Resolution (2026-08-30)

Phase 1 (structural forest map + forest prereq validation) complete: generate_global_map.py + GlobalMapView/DomainCard + build_forest_index/validate_forest + check-maps-forest gate + overlay.status_map_for_map extraction. Also fixed a stale parent (storage-and-table-formats → data-analytics) the map exposed. All 8 Phase-1 AC met. The 2 Phase-2/3 AC (computed concept edges; lazy detection) are intentionally split into #266/#267 per the research (similarity edges are low-precision on a small corpus → author-confirmed suggestions, deferred). Closing this feature ticket at Phase-1 scope with follow-ups tracked.
