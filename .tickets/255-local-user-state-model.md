---
id: "255"
title: "Minimal per-user overlay: gitignored sparse status map keyed by node ID"
status: done
blocked_by: ["258"]
priority: high
tags: ["platform"]
---

# Minimal per-user overlay: gitignored sparse status map keyed by node ID

## Why (this is the FLOOR, deliberately minimal)

Per owner direction (2026-08-29): the committed content graph is the first-class citizen
(#257); per-user state is a THIN, gitignored overlay whose only job is to keep user
state out of the committed tree, keyed back to the graph's node IDs. **No event-sourcing,
no serve write-API, no sync bridge** — that apparatus is deferred to #259 (backlog) and
nothing here depends on it. A user's overlay is just their local file; losing it is
acceptable (delete = reset progress).

This is the concrete store that #258's overlay-interface calls
(`overlay.get(node_id) -> {status, updated_at} | None`, `overlay.set(node_id, status)`).

## Findings (research + review, 2026-08-29 — #258 already delivered the store)

#258 shipped `tools/lib/overlay.py` + the ULID-keyed `.user/status-overlay.json` store,
the `load/get/set/reset` interface, serve endpoints, `.user/` gitignore (any depth), and
fresh-clone behavior. So AC 1,3,5,6,7 are DONE. Only AC 2 (SR relocation) + AC 4 (prereq
indicator) remain. Evidence: `.scratch/review/sr-relocation-blast.md`,
`.scratch/review/prereq-indicator-surface.md`, `.scratch/research/sr-key-strategy.md`,
`.scratch/research/prereq-indicator-ux.md`.

### SR stays SLUG-keyed — do NOT re-key cards to ULID (locked by evidence)
Anki/FSRS separate an immutable card GUID from the mutable topic label; scheduling hangs
off the stable id, never the name. Re-keying existing cards SILENTLY RESETS FSRS/SM-2
state (the documented Anki import-collision failure). So "keyed by node id" is satisfied
at the JOIN boundary: overlay=ULID-keyed; SR cards keep uuid4 id + slug/lesson_id and join
to the graph via the slug↔ULID map the parser already provides. Full card re-keying is
undesirable and belongs in #259 if ever.

### SR relocation = one-point centralization (NOT N-point)
Path hardcoded in 11 sites / 8 files; `questions.py` is the intended resolver (#107; 6
tools already import from it). Add a resolver preferring `<ws>/.user/learning-records/`
(per-user, gitignored) with FALLBACK to `<ws>/learning-records/` for READ — because the 9
committed `examples/*/learning-records/` files are demo FIXTURES and MUST stay committed
(moving them under `.user/` would gitignore + break them). Convert the 7 hardcoders:
check-topic-completeness, generate-quiz-page, generate_map_page, backfill-criteria,
verify-links, init_workspace, serve.py. Zero test blast radius; no .gitignore change.
serve.py `/api/questions` uses the resolver; confirm `.user/` isn't browsable if private.

### Prereq indicator = no new fetch (data already client-side)
Each topic ships `prereqs` as resolved ULIDs + its own `status` in the island; every
prereq's live status signal is already hydrated in store.js (ULID-keyed). Edit
`TopicCard.js` (prereqText block L13-19): met = prereq status complete|in-progress. NO
gating (topic stays clickable). UX: filled ✓ met / outline ○ not-yet — NOT padlock/grey/
red. Accessibility: pair color with glyph+word (StatusBadge precedent; color-not-alone is
a hard rule). CSS in generate_map_page.py `css_extra` (map-card CSS is island-local).

## What to build

### 1. Overlay files (gitignored)
- **Progress overlay** — a single sparse JSON map keyed by the ULID node id:
  ```json
  { "schema": 1,
    "overlay": {
      "01J...metadata": { "status": "complete",    "updated_at": "2026-08-29T14:00:00Z" },
      "01J...ingest":   { "status": "in-progress", "updated_at": "2026-08-29T14:20:00Z" } } }
  ```
  Absent key = not-started. `status ∈ {not-started, in-progress, complete}` (read =
  "in-progress" is fine; keep the current lenient semantics). Location: `.user/` (ADR
  0012 private path), gitignored.
- **Quiz/SR state** — per-user, keyed by the SAME node ids (and card id where relevant),
  in a SEPARATE gitignored file under `.user/`. Keep it simple: the existing
  `learning-records/{questions,reviews}` shapes relocated under `.user/`, keyed by node
  id. No log-inversion (that's #259).

### 2. Overlay interface (used by #258's queries/endpoints)
- `overlay.load()` → sparse dict; `overlay.get(node_id)`; `overlay.set(node_id, status)`
  (stamps `updated_at`); `overlay.reset()` (delete file). Pure stdlib, on-disk JSON.
- serve.py status GET/POST (reworked in #258) read/write via this interface.

### 3. `.gitignore`
- Ensure `.user/` is gitignored (coordinate with #183/#184 which also touch `.user/`).

## Prereqs are INFORMATIONAL only (locked decision)
Do NOT gate/lock topics on prereqs. The overlay + graph together power a simple
"recommended prereqs: ✓ met / ○ not yet" indicator per topic (met = the prereq node's
overlay status is complete/in-progress). No availability locking, no blocked topics.

## Depends on
- **#258** (status removed from committed graph; readiness queries take the overlay arg).
  Transitively needs #257 (ULID node ids — the overlay's keys).

## Out of scope (moved to #259, backlog)
- Event-sourced review log, serve write-API beyond simple status GET/POST, browser
  IndexedDB store, export/import bridge, cross-device sync, File System Access API.

## Acceptance criteria

- [x] A gitignored `.user/` overlay stores `{node_id → {status, updated_at}}` (sparse) — #258
- [x] Quiz/SR per-user state relocated under `.user/learning-records/` (per-user); status
      overlay is node-id-keyed; SR stays slug-keyed and joins to the graph via slug↔ULID
      (re-keying cards is harmful per Anki/FSRS evidence — deferred to #259). No committed
      per-user state (live workspace + `.user/` both gitignored; only demo fixtures committed)
- [x] Overlay interface (`load/get/set/reset`) is pure stdlib on-disk JSON; #258's
      queries + serve endpoints use it — #258
- [x] Topic view shows recommended-prereq met/unmet indicator (informational, no gating) —
      Playwright: `✓ met` / `○ not yet` glyph+word, cards stay interactive, `/.user/` 404
- [x] Fresh clone (no `.user/`) = all topics not-started, nothing errors; deleting
      `.user/` resets progress cleanly — #258 fresh-clone sim + resolver default
- [x] `.user/` is gitignored; `git status` clean after marking topics complete
- [x] `mise run verify` EXIT 0

## Validation

Mark topics complete → writes only to `.user/`, `git status` clean; delete `.user/` →
progress resets, no errors; a topic with an unmet recommended prereq shows the ○
indicator but is still fully accessible (no gating).

## Resolution (2026-08-29)

Minimal per-user overlay floor completed (store shipped in #258). SR/quiz store relocated to .user/learning-records/ via a one-point resolver in questions.py (prefer private .user/, fall back to committed example fixtures for read); 7 path-hardcoders converted; init_workspace scaffolds the private path; serve.py /api/questions uses the resolver and a new /.user/ 404 guard keeps the overlay non-browsable. SR cards stay slug-keyed (re-keying resets FSRS state per Anki evidence; node-id join at the graph boundary only; full re-key deferred to #259). Non-gating recommended-prereq indicator added to TopicCard.js (✓ met / ○ not yet from live overlay-backed status signals, no fetch, color+glyph+word), CSS in generate_map_page css_extra. Validated via mise verify+check-maps, SR resolver checks, and Playwright (indicator states, non-gating, privacy guard).
