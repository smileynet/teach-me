---
id: "257"
title: "First-class committed graph schema: ULID node IDs + typed why-annotated edges"
status: open
blocked_by: ["256"]
priority: high
tags: ["platform"]
---

# First-class committed graph schema: ULID node IDs + typed `why`-annotated edges

## Why (the primary goal)

The product goal is to present content cleanly and highlight the RELATIONSHIPS between
topics — a discoverable prerequisite/leads-to/related GRAPH, not a linear course. The
COMMITTED graph is the first-class citizen and deserves a real schema. Prior art
(research 2026-08-29, `.scratch/research/committed-authored-formats.md` +
`committed-discoverability.md`) is unanimous:

- One node per file/section; **edges embedded in frontmatter keyed by a stable ID**;
  the graph is a rebuildable projection of git (Astro content collections, Dendron,
  Obsidian, Foam).
- Durable-graph tools **decouple an immutable ID from the mutable slug/filename**
  (Dendron autogenerates an opaque frontmatter id, forbids editing it) — validates the
  ULID+slug decision. Filename-as-ID and separate edge-files are named anti-patterns.
- **Typed, `why`-annotated edges** are what make relationships discoverable; an untyped
  hairball destroys discovery. Author forward edges + intent; DERIVE backlinks,
  readiness, order, "next", stats.

Decisions locked (ADR-0014, this epic): ULID ids + mutable slug; edge types `prereq`
(informational, met/unmet, no gating) | `leads_to` (navigational) | `related`
(symmetric, NEW — the clearest discoverability gap); readiness/order/next are DERIVED,
never stored.

## Current schema (verified, `tools/map_parser.py`)

- `Topic` (L19-27): `slug`(20, the ONLY identity today), `title`, `why`, `scope`,
  `prereqs: list[str]`(24, untyped slug list), `status`(25, per-user — removed in #258),
  `lesson_file`. No stable ID.
- `LeadsTo` (L30-33): `slug`, `why` — labeled but DOMAIN-level only.
- Edges are untyped (prereqs) or domain-scoped (leads_to); no topic-level `related`.

## What to build

### 1. Stable ULID identity + slug indirection
- Add `id: str` (ULID) as the first field of `Topic`; `slug` becomes mutable
  display/routing only. Authoring contract: `id` is generated once, never hand-edited
  (validate rejects mutation).
- Author edges by slug in MAP.md for human friendliness, but **resolve slug→id at parse
  time** and store ID endpoints on the in-memory model. Build `id→Topic` and `slug→id`
  indexes in `load_map`; add `topic_by_id`.

### 2. Typed, `why`-annotated edges (first-class)
- Introduce `Edge {source_id, target_id, type, why}` with
  `type ∈ {prereq, leads_to, related}`. Unifies today's `prereqs` (untyped) and
  `LeadsTo` (domain-only). `prereq` edges gain a `why` for free.
- `related` is symmetric — store once, surface both directions (derive the inverse).
- Keep `leads_to` distinct from a prereq inverse (it is navigational, cross-domain).

### 3. Validation (extend `validate`)
- id uniqueness + ULID format; slug uniqueness.
- Typed-target resolution: every edge target id must exist.
- Cycle detection on `prereq` edges ONLY (leads_to/related are exempt — they may be
  cyclic/navigational). Preserve the current Kahn check, scoped to prereq edges.

### 4. Migration + emitters
- Mint ULIDs for existing topics; add `- **id:** <ULID>` to every committed
  `examples|library/**/*.MAP.md` topic block; resolve existing prereq slugs to ids.
- Update MAP.md authoring emitters to write `id:` and typed edges:
  `tools/map_from_deps.py` (~L350-360), `tools/map_from_chunks.py` (~L180-181),
  `tools/enrich_prereqs.py` (~L97-131, map detected slugs→ids before writing).

### 5. Consumers (blast radius — verified `.scratch/subagent-raw/review-graph-consumers.md`)
- `serve.py GET /api/map/{domain}` (~L388-416): emit `id` + typed edges; routes stay
  slug-keyed (resolve slug→id server-side).
- Client: `MapView.js` (~L44,47) keys dagre by `t.id` and edges by prereqs —
  **prereq endpoints MUST be in the same id-space as `t.id`** or dagre draws no edges;
  `TopicCard.js` (~L14) resolves prereqs via `find(t.id===p)`. Migrate edges to ids.
  `leads_to` keeps slug for `-map.html` routing.
- Lesson↔node link is slug-from-filename (`slug in f.stem`) — ULID only fixes
  rename-breakage if lessons carry the id; document this (full lesson-id carry is a
  follow-up, not required here).

## Depends on
- **#256** (single parser) — so this schema change is a one-site edit, not a triple-edit.

## Out of scope
- Removing `status` from the committed file (#258 — this ticket keeps status readable
  during the transition, just adds id + typed edges).
- The minimal user overlay (#255).

## Acceptance criteria

- [ ] `Topic` has an immutable `id` (ULID); `slug` is display/routing only
- [ ] Committed edges are typed `{source_id, target_id, type, why}` with
      `type ∈ {prereq, leads_to, related}`; `related` supported end-to-end
- [ ] Edges reference IDs (slug→id resolved at parse time); a slug rename touches only
      that node's frontmatter, no edge rewrites
- [ ] `validate`: id-uniqueness + ULID format, slug-uniqueness, edge-target resolution,
      cycle-detection on `prereq` edges only
- [ ] All committed MAP.md files carry `id:` per topic; emitters
      (map_from_deps/chunks, enrich_prereqs) write id + typed edges
- [ ] Map page renders edges by type (informational prereq vs navigational leads_to vs
      related) with distinct styling; dagre edges intact (id-space consistent)
- [ ] `mise run verify` EXIT 0; tests updated for the new schema

## Validation

`mise run verify` green; regenerate maps and confirm typed edges render + dagre edges
present; rename a topic's slug and confirm no edge breaks (id-keyed); `validate` catches
a duplicate id, a bad ULID, and a prereq cycle.
