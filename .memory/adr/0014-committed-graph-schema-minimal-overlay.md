# 0014 — First-class committed content graph + minimal per-user overlay

**Status:** proposed
**Date:** 2026-08-29

## Context

ADR 0012 established the two-tier content model (committed public library + gitignored
per-user state). This ADR decides the *schema* for both tiers, driven by the product
goal restated 2026-08-29: **present content cleanly and highlight the RELATIONSHIPS
between topics** — a discoverable prerequisite/leads-to/related GRAPH, not a linear
course. The committed graph is the first-class citizen; per-user state is a thin overlay.

Three rounds of dispatched research + code review (2026-08-29) informed this
(`.scratch/research/graph-*.md`, `committed-*.md`, `overlay-*.md`;
`.scratch/subagent-raw/review-graph-*.md`):

- **Overlay model (ITS, Carr & Goldstein 1977; Khan Academy):** a shared domain model
  (the graph) + a thin per-user learner model (values keyed by node id). Readiness is a
  DERIVED predicate, never a stored field. [L4, multiple agreeing]
- **Authored graph formats (Astro content collections, Dendron, Obsidian, Foam):** one
  node per file/section; edges embedded in frontmatter keyed by a stable ID; the graph
  is a rebuildable projection of git. Durable-graph tools decouple an immutable ID from
  the mutable slug/filename (Dendron autogenerates an opaque id, forbids editing it).
  Filename-as-ID and separate edge-files are named anti-patterns. [L4]
- **Discoverability:** typed, `why`-annotated edges make relationships legible; an
  untyped hairball destroys discovery. Author forward edges + intent; DERIVE backlinks,
  readiness, order, "next", stats. [L4]

Current state (verified, `tools/map_parser.py`): `slug` is the ONLY node identity and is
the primary key for edges, routes, and file-matching; `prereqs` is an untyped slug list;
`leads_to` is labeled but domain-scoped only; per-user `status` is authored INTO the
committed MAP.md and written back by the server and at generate time. Three independent
MAP.md parsers exist (canonical + two regex shadows), so any schema change risks drift.

## Decision

### A. Committed graph is first-class (the priority)

1. **Immutable ULID node IDs + mutable slug.** Every topic gets an opaque `id` (ULID),
   generated once, never hand-edited. `slug` is display/routing only. Edges reference
   IDs (authored by slug, resolved slug→id at parse time), so a rename touches only that
   node's frontmatter. (#257)
2. **Typed, `why`-annotated edges** as a small closed vocabulary:
   - `prereq` — INFORMATIONAL only (met/unmet indicator, **no gating/locking**).
   - `leads_to` — NAVIGATIONAL (ranks suggestions; does not gate; may cross domains).
   - `related` — symmetric adjacency (NEW; the clearest discoverability gap). Store once,
     derive the inverse.
   Cycle detection applies to `prereq` edges only.
3. **Derive, don't store.** Readiness, topological order, "next suggestion", backlinks,
   and progress% are computed at runtime from (committed edges ⋈ overlay). Nothing
   derived is written onto the committed node.
4. **One parser.** Collapse the three MAP.md parsers to `map_parser.load_map` first
   (#256), so the schema change is a single-site edit.

### B. Per-user state is a minimal gitignored overlay (the floor)

5. **Sparse status overlay** keyed by node id: `{node_id → {status, updated_at}}` under
   `.user/` (ADR 0012 private path), gitignored. Absent = not-started. Quiz/SR per-user
   state relocates under `.user/`, keyed by the same node ids. (#255)
6. **No sync apparatus.** No event-sourcing, no serve write-API beyond simple status
   read/write, no browser store, no export/import bridge, no cross-device sync. A user's
   overlay is just their local file; losing it is acceptable. The richer apparatus (from
   the sync research) is captured in #259 as **backlog** with nothing depending on it.

### C. Prereqs are informational

7. Do not compute "available/locked" topics from prereqs. Surface a simple "recommended
   prereqs: ✓ met / ○ not yet" indicator (met = prereq node's overlay status is
   complete/in-progress). All topics remain fully accessible.

## Consequences

**Easier:**
- Relationships become first-class and discoverable (typed `why`-annotated edges,
  `related` adjacency) — directly serves the product goal.
- Slug renames stop breaking the graph (edges key on ULID).
- Per-user state leaves the committed tree; a fresh clone shows all topics at zero
  progress; committed maps stop churning with personal state.
- Collapsing to one parser removes the silent-drift risk before the schema changes.
- Deferring the sync apparatus keeps scope proportional to the SECONDARY priority of SR.

**Harder / risks:**
- Broad blast radius (verified): ULID + status-removal touch map_parser, serve.py, two
  page generators, MapView/TopicCard/store/LessonActions clients, completeness checker,
  three MAP.md emitters, and the test fixtures. Sequencing (#256→#257→#258→#255) contains
  this, but it is multi-ticket.
- Two silent-failure traps to guard: the index progress ring and completeness checker
  read committed `status` via regex (return 0 once it's gone); client dagre edges use
  `t.id` for both node keys and prereq endpoints (edges vanish if id→ULID but prereqs
  stay slugs). Both are called out in #257/#258 AC.
- Lesson↔node links are slug-from-filename; ULID only fixes rename-breakage if lessons
  carry the id (a documented follow-up, not required now).
- `related` adds authoring surface; kept optional and cheap since edges are being
  reworked anyway.

## Implemented by
- **#256** unify parsers → **#257** ULID + typed edges → **#258** remove committed status
  → **#255** minimal overlay. **#259** (backlog) optional SR sync, deferred.
- Independent of the #183 `examples/`→`library/` rename (schema, not paths) — both tracks
  proceed in parallel.
