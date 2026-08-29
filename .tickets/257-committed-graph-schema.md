---
id: "257"
title: "First-class committed graph schema: ULID node IDs + typed why-annotated edges"
status: done
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

## Implementation plan (research-backed 2026-08-29)

Three research tracks + a code-review edit plan
(`.scratch/research/257-*.md`, `.scratch/subagent-raw/257-editplan.md`) resolved the
open implementation questions:

### Decisions locked
- **ULID = vendored stdlib module** `tools/lib/ulid.py` (~40 lines: `new`/`is_valid`/
  `parse`), NO dependency. IDs minted rarely (authoring/migration), stored as the
  26-char string in git; runtime is parse/validate-dominated. Spec-compliant → escape
  hatch to `python-ulid`/stdlib `uuid7` stays open. (Rejected nanoid/uuid4: unsortable;
  uuid7: needs py3.14, we're on 3.12.)
- **Typed-edge authoring = a `## Edges` markdown section** (NOT inline `prereqs`).
  Block-style list of `{from, to, type, why}` authored BY SLUG (human-writable),
  resolved to IDs at parse time. Chosen because the per-topic `_FIELD_RE` only captures
  single-line fields — a `## Edges` section keeps `_FIELD_RE` untouched and reuses the
  proven `_parse_frontmatter` nested-object logic (same machinery as `leads_to`). Makes
  `related` first-class + carries per-edge `why`. Example:
  ```
  ## Edges
  - from: iceberg-metadata
    to: table-format
    type: prereq
    why: understand the on-disk layout before metadata makes sense
  ```
- **Migration = idempotent backfill + slug→id resolution + reserved `aliases:`.** The
  data (presence of `- **id:**`) is the idempotency key — re-run = empty git diff. Edges
  stay authored by slug; MAP.md never contains a ULID in an edge. Renames add old slug to
  a per-topic `aliases:` list (id unchanged → references still resolve).

### The silent-failure trap (gate on VISUAL verification)
`generate_map_page.py:270` (`"id": t["slug"]`) is the one line making id==slug today.
`MapView.js:63` does `g.setEdge(p, t.id)` — matches only because id IS the slug. When id
becomes a ULID but prereqs stay slugs, dagre SILENTLY creates phantom nodes and edges
detach (no error). Fix: emit id-keyed prereqs/edges in the island; verify arrows land on
cards (`mise run visual-qa`), not "it ran." Cycle-check MUST scope to `type=="prereq"`
or symmetric `related` edges false-positive as cycles. (`store.js`/`GenButton` state flow
verified SAFE — keyed by `topic.id` end-to-end, no slug-keyed caller.)

### Subtasks (order A→B→C, D last; each shippable + verifiable)
- **A — schema + parser** (`tools/lib/ulid.py` + `map_parser.py`): `Edge{source_id,
  target_id,type,why}` + `EDGE_TYPES=("prereq","leads_to","related")`; `Topic.id`;
  `DomainMap.edges` + `topic_by_id`; parse `## Edges`; synthesize edges via slug→id;
  cycle-check scoped to `prereq`; repoint `get_available_topics`/`get_next_suggestion`
  to id-keyed prereq edges; endpoint + edge-type validation. Gates the rest.
- **B — migration** (`tools/migrate_map_ids.py`): idempotent ULID backfill into committed
  MAP.md; verify run-twice = 0 minted, git diff = id-line insertions only.
  - **B technique (validated 2026-08-29, prototyped against all 9 maps → 59 ids,
    idempotent, CRLF preserved):** SURGICAL raw-text insert, NOT parse+reserialize (even
    ruamel isn't diff-clean → breaks the empty-diff proof). Read `read_bytes().decode`,
    `re.sub` on header `^(### )([^\r\n]+?)([ \t]*)(\r?\n)`; probe the block for a valid-ULID
    id line (skip) else append `- **id:** {ulid.new()}` reusing the block's OWN newline
    (group 4) so mixed CRLF/LF is preserved (`blender-texture-prep.MAP.md` is the lone LF
    file). Insert as the FIRST field after the header (field ordering/sets vary per block).
    Guard with `_write_lock`; atomic write via temp + `os.replace`; dry-run default, `--apply`
    to write; flag an existing-but-invalid id for manual review (don't duplicate). Standalone
    `tools/migrate_map_ids.py` (not a map_parser flag). Add a unit test (idempotency +
    CRLF/LF preservation).
- **C — client render** (`generate_map_page.py` island + `MapView.js`/`TopicCard.js`):
  emit `id`(ULID)+`slug`+id-keyed edges array; style by type (prereq solid/related
  dashed). Verify via `visual-qa` — edges land on cards.
- **D — emitters + close A's soft_prereqs loop** (resolved 2026-08-29):
  - **Decision: `soft_prereqs` → `related` edges** (symmetric, non-gating). Prior art
    (KnowLP dual prereq/similarity graph, arXiv 2506.22303; K12-KGraph `relates_to`):
    a soft prereq isn't a weak prereq (removing gating removes what makes it a prereq) —
    it's an associative link, which is exactly our `related` type. NOT a weighted prereq,
    NOT a 4th type.
  - **`load_map` (finishes Subtask A's open edge):** add `Topic.soft_prereqs` (parsed like
    `prereqs`); synthesize symmetric `related` edges from inline `soft_prereqs` (reuse the
    `_add_edge` + reverse-derive path). `related` edges are excluded from the prereq
    cycle-check (already scoped). Add a load_map test: a `soft_prereqs` entry → a `related`
    edge, not a prereq.
  - **Emitters:** `map_from_deps.py` inject `- **id:** {ulid.new()}` after `### {slug}`
    (~:391; `from lib import ulid` — sys.path set at :26); `map_from_chunks.py` inject after
    `### {slug}` (:176; needs the GUARDED `try: from tools.lib import ulid / except: from lib`
    import — no top-level sys.path insert, imported as `tools.map_from_chunks`). Inline
    prereqs/soft_prereqs STAY (load_map derives edges from them — no `## Edges` needed).
    `map_from_chunks._validate_output` still passes with ids (verified).
  - **`enrich_prereqs.py`: NO change** — verified id lines pass through untouched (line-walk
    only special-cases `###`/`prereqs`/`soft_prereqs`; id line copied verbatim). Do NOT mint
    ids in enrich (it splits/joins on `\n` → EOL-churn risk; minting stays in emitters +
    migrate_map_ids.py).
  - **Verify:** `_validate_output` round-trips; regenerate a fixture → soft_prereqs produces
    a `related` edge (not prereq, not cycle-checked); `mise run verify` EXIT 0.



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

## Resolution (2026-08-29)

First-class committed graph schema delivered in 4 subtasks (A schema/parser, B ULID migration, C client render, D emitters + soft_prereqs->related). Nodes carry immutable ULID ids + mutable slug; edges are typed {prereq|leads_to|related} keyed by id, resolved from slug at parse time; readiness/order derived. NOTE: AC 'enrich_prereqs write id' was delivered as PASS-THROUGH (verified untouched), not minting — per Subtask D research, minting stays in the generating emitters (map_from_deps/chunks) + migrate_map_ids.py to avoid enrich's \n-join EOL churn; enrich never needs to mint since it edits already-committed (already-id'd) maps. Unblocks #258 (remove committed status) -> #255 (minimal overlay). Pre-existing cross-map dangling prereqs tracked separately in #260.
