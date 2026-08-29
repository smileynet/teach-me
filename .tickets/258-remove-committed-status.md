---
id: "258"
title: "Remove per-user status from the committed graph (readiness derived from overlay)"
status: in_progress
blocked_by: ["257"]
priority: high
tags: ["platform"]
---

# Remove per-user `status` from the committed graph

## Why

Today `Topic.status` (not-started|in-progress|complete) is authored INTO the committed
MAP.md and written back into it by the server and at page-generation time — per-user
state living in the shared, versioned tree. ADR 0012 / ADR-0014: the committed graph is
shared; per-user state is a gitignored overlay. This ticket severs the leak. Readiness
is DERIVED at runtime by joining the committed edges with the overlay (the overlay
itself is #255).

## The leak — three write paths into the committed file (verified)

1. `map_parser.update_status` (~L296-337) — regex-rewrites `- **status:**` in MAP.md.
2. `serve.py POST /api/map/{domain}/{slug}/status` (~L440-454) — calls `update_status`.
3. `generate_map_page.py` `compute_effective_status` → `update_status` write-back
   (~L230-247) — syncs disk-derived status into MAP.md at generate time.

## What to build

- **Delete `status` from `Topic`** and from `load_map`'s read; delete the status
  value-check in `validate`.
- **Rewrite readiness queries to take the overlay as an argument:**
  `get_available_topics(domain_map, overlay)` and `get_next_suggestion(domain_map,
  overlay)` — join `{node_id → status}` at runtime, never read status off the node.
- **Replace `update_status`** with an overlay writer that touches ONLY the gitignored
  overlay (keyed by node_id/ULID), never MAP.md.
- **serve.py:** status GET/POST endpoints read/write the overlay (resolve slug→id
  first); `GET /api/map` joins overlay status onto committed topics.
- **generate_map_page.py:** `compute_effective_status` still derives from disk but
  writes to the overlay (or is dropped from committed generation); kill the
  "trust `complete` from MAP.md" branch.
- **Fix the silent-failure consumers** (they read committed status via regex and will
  silently return 0 once it's gone):
  - `generate_index_page.py` progress ring (~L84-89) → count from the overlay.
  - `check-topic-completeness.py` `get_topics_from_map` (~L238-260, filters
    `status=="complete"`) → read overlay (or drop the gate).
- **Migration:** strip `- **status:** ...` from all committed
  `examples|library/**/*.MAP.md`; stop emitters (map_from_deps/chunks) from writing it
  (already covered where those emit `id:` in #257 — confirm status line removed).
- **Client:** `store.js` seeds status from an overlay fetch (or the joined `/api/map`
  payload) instead of the data island; `LessonActions.js`/`GenButton.js` writes hit the
  overlay-backed endpoint (no committed status lands). Keying by `t.id` (ULID) is fine.

## Blast radius (verified 2026-08-29 — full inventory beyond the three write-paths)

Codebase review found status touches 30+ points. Research confirmed the target design
(sparse overlay keyed by immutable ULID, join-at-runtime, absent-key = not-started)
matches the xAPI/SCORM standard. Full inventory: `.scratch/review/status-writepaths.md`.

- **Emitters also write the status line** (not just the 3 write-paths):
  `map_from_chunks.py:187` and `map_from_deps.py:365` both emit
  `- **status:** not-started` — stop emitting.
- **Client seeding chain** carries committed-derived (soon-stale) status:
  `preact_page.py:69` data island → `MapView.js:80` → `store.js` `initTopicStates`.
  Seed from the overlay-joined `/api/map` payload instead. `LessonActions.js` GET/POST
  and `GenButton.js` flow through the endpoints being changed (API contract holds — no
  logic change). `StatusBadge.js`/`TopicCard.js` are pure render (no change).
- **Skill docs** instruct committed writes: `generate-topic/SKILL.md:58,62,64`
  (calls `map_parser.update_status`, reads status from MAP.md) → overlay writer/read.
- **9 committed MAP.md** files carry status lines to strip. Migration must be
  **idempotent** (remove-if-present; second run is a no-op).
- **Fail-loud discipline** (migration research): the two silent-0% consumers are the
  classic `.get(key,0)` trap — read overlay explicitly, and after strip grep-prove
  ZERO committed readers of `**status:**` / `Topic.status` remain.
- **Tests to update:** `test_map_parser.py`, `test_map_page.py`, `test-navigation.py:161`,
  `tests/test_map_from_chunks.py:57`, `check-map-edges.py:171-172` fixture strings.

### Overlay module (this ticket ships the minimal interface #255 fills in)
Green field: no `overlay.py`/`.user/`/`progress.json` exists; `tools/lib/ulid.py` is the
key provider. Ship `tools/lib/overlay.py` with the LOCKED signatures so #255 drops in:
`load() / get(node_id)->{status,updated_at}|None / set(node_id,status) / reset()`.
Constraints: key by ULID node id (NOT slug — serve resolves upstream); absent key =
not-started; `get`→None on absent (don't materialize on read); do NOT name the file
`progress.json` (use `.user/status-overlay.json`, #255 finalizes); do NOT reuse the
name `update_status`; add `/.user/` to `.gitignore` ONCE (triple-claimed by #255/#183/#184).

### Coordination flagged for #255 (do NOT solve here)
- `Card.id` is `uuid4`, not ULID — SR state relocated under `.user/` must join to the
  graph by topic ULID (via `lesson_id`/topic mapping), not `Card.id`.
- Markdown insight records (`learning-records/NNNN-slug.md`) share the dir with JSONL
  SR stores; relocation fate unspecified — #255 owner's call.

## Depends on
- **#257** (ULID ids + typed edges) — the overlay keys on node_id, and readiness walks
  id-based edges.

## Out of scope
- The overlay schema/store itself (#255 — this ticket assumes an overlay interface the
  queries/endpoints call; #255 provides the concrete minimal store). Coordinate the
  interface: `overlay.get(node_id) -> {status, updated_at} | None`, `overlay.set(...)`.

## Acceptance criteria

- [ ] `status` removed from `Topic` and from every committed MAP.md (9 files)
- [ ] No code path writes per-user status into the committed tree (`update_status`
      committed-file writer gone; serve POST + generate-time write-back go to overlay;
      `map_from_chunks`/`map_from_deps` emitters stop emitting the status line)
- [ ] `tools/lib/overlay.py` ships the locked interface (`load/get/set/reset`, ULID keys,
      sparse, stdlib JSON, absent=not-started, get→None on absent)
- [ ] `get_available_topics`/`get_next_suggestion` take the overlay as an argument;
      readiness is derived, node carries no status
- [ ] Index progress ring and `check-topic-completeness` read the overlay (no silent 0%)
- [ ] Client seeds status from the overlay-joined `/api/map` payload (island no longer
      the status source of truth)
- [ ] `generate-topic/SKILL.md` no longer instructs committed status writes/reads
- [ ] `/.user/` added to `.gitignore`; migration is idempotent
- [ ] Grep proof: zero committed readers of `**status:**` / `Topic.status` remain
- [ ] Fresh clone (no overlay) shows all topics with zero completion, nothing errors
- [ ] `mise run verify` EXIT 0; tests updated (no `Topic(status=...)`)

## Validation

Fresh-clone simulation (delete overlay) → map/index render all topics at 0% with no
error; mark a topic complete → written ONLY to the gitignored overlay, `git status`
clean of committed changes; `mise run verify` green.
