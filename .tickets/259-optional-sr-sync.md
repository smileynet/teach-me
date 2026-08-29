---
id: "259"
title: "Optional SR state sync: event-sourced store + serve write-API + export/import bridge"
status: backlog
priority: medium
blocked_by: []
tags: ["platform"]
---

# Optional SR state sync (DEFERRED — nothing depends on this)

## Status: backlog / optional

Per owner direction (2026-08-29): quiz/SR is SECONDARY to presenting the committed
content graph cleanly. The minimal overlay (#255) is the floor — a user's per-topic
state is just their local gitignored file; losing it is acceptable. This ticket captures
the RICHER sync apparatus from the sync research
(`.scratch/research/overlay-*.md`, `overlay-bridge.md`, `overlay-local-first.md`) so the
findings aren't lost — but it is NOT on the frontier and nothing blocks on it. Pull it
onto the board only if cross-device / static-Pages SR sync becomes a real need.

## What it would build (if ever prioritized)

1. **Event-sourced SR store (invert log↔state).** Today `questions.py::review_card`
   makes card-embedded `schedule` authoritative and rewrites the topic file; the review
   log is a lossy secondary audit trail (no stable event id). Invert it: `reviews.jsonl`
   with a stable ULID `event_id` becomes authoritative; card schedule is a deterministic
   FOLD of the log (`sm2.review()` is already a pure function — replay-capable). REQUIRES
   a spike first to prove replay reconstructs current state exactly.
2. **serve.py overlay write-API** (localhost-bound ONLY — a write endpoint on
   `serve:lan` 0.0.0.0 is a foot-gun): `GET /api/overlay` (server folds JSONL→state),
   `POST /api/overlay/events` (append-only, verbatim, ULID-keyed for idempotency).
3. **Browser store + static fallback:** localStorage for the bounded progress map,
   IndexedDB for the unbounded review log; `navigator.storage.persist()` once;
   feature-detect the serve API (present → connected/server-authoritative; absent on
   Pages → browser-only).
4. **Export/import bridge** (`tools/overlay_sync.py`): one `overlay.json`, ULID-keyed;
   LWW-by-timestamp for scalar state, UNION-by-event-id for the review log (additive,
   idempotent); fold into existing `questions/{topic}.jsonl` + `reviews.jsonl` so the
   CLIs stay unchanged. File System Access API as a Chromium-only convenience.

## Merge contract (from research, if built)
Progress map: LWW per node_id by `updated_at`. SR current state: LWW per
(node_id, card_id). Review log: set-union deduped by ULID event_id, NEVER LWW. ISO-8601
UTC timestamps; schema-version tag with refuse-newer. The robust conflict fix (same card
reviewed on Pages AND CLI) is to recompute state by replaying the merged log — hence the
event-sourcing prerequisite.

## Why deferred
- The minimal overlay (#255) already gives per-user state out of the committed tree.
- No cross-device requirement exists yet; a single local file is sufficient.
- The apparatus is substantial (spike + 3-4 features) and serves the SECONDARY goal.

## Acceptance criteria (only if pulled onto the frontier later)

- [ ] Spike proves `reviews.jsonl` replay reconstructs current card state exactly
- [ ] Event-sourced store: log authoritative, state is a rebuildable fold, stable event ids
- [ ] serve.py overlay API, localhost-bound; browser store with static fallback
- [ ] `tools/overlay_sync.py` round-trips overlay.json ↔ JSONL; CLIs unchanged
- [ ] Merge: LWW scalars, union-by-event-id log; `mise run verify` EXIT 0
