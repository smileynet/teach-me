---
created_at: 2026-08-29T11:20:00-07:00
base_commit: 9160976
handoff_key: content-graph-schema
---

# Handoff

> Supersedes the `ink-godot-track` handoff. This session built the ADR-0014 content model.

## Objective
Make the committed topic GRAPH first-class (ULID ids + typed edges) and per-user state a
thin gitignored overlay. Tracked in tickets (NO PLAN.md — `tkt ready` is authoritative).

## Constraints
- No PLAN.md; `tkt sync-plan` N/A. `tkt` via `D:\code\tkt\target\release\tkt.exe`.
- Python via `.venv\Scripts\python.exe` directly (mise shim recursion). Windows-first.
- `tkt close --check-all --evidence ... --resolution ...` WORKS (closed 4 this session) —
  the AGENTS.md "hand-edit status:done" instruction is STALE (see #263).
- AGENTS.md at 150/150 (ceiling) — route new gotchas to `.memory/specs/`, not AGENTS.md.
- Pre-existing ink-test-project/test-scene churn in `git status` is #234/#233's, NOT ours.

## Prior Decisions (ADR-0014, accepted)
- Overlay model: committed graph + thin per-user overlay, joined at runtime.
- Node id = immutable ULID (`tools/lib/ulid.py`, vendored) + mutable slug (display/route).
- Edges typed + closed vocab: `prereq` (informational, no gating), `leads_to` (nav),
  `related` (symmetric; `soft_prereqs`→related). Cycle-check scoped to prereq only.
- Readiness/order/next/backlinks DERIVED at runtime, never stored.
- Minimal overlay is the floor; SR sync apparatus deferred (#259 backlog).

## Current State
#257 (schema) fully DONE across subtasks A–D + hardened by #261 (all closed, pushed).
`map_parser.load_map` is the single MAP.md parser; all 9 committed maps carry stable
ULIDs; map render is ULID-keyed with `data-*` test contract; `mise run check-maps` gates
edge connectivity (identity-first, negative-tested). Nothing mid-flight — clean stop.

## Next Steps
Frontier (`tkt ready`): **#258** (remove per-user `status` from committed MAP.md —
sever the 3 write-paths: `map_parser.update_status`, serve.py POST status, generate-time
write-back; make `get_available_topics`/`get_next_suggestion` take the overlay arg) →
then **#255** (minimal `.user/` overlay). Parallel: **#183** (examples/→library/ rename).
Use the research→review→build→verify→close pattern that worked all session.

## Fog
- #258/#255 need an overlay INTERFACE contract (`overlay.get/set(node_id)`) agreed between
  them — #255 provides the store, #258 calls it. Define the interface before starting #258.
- #260 (cross-map dangling prereqs: toon-banding/configurable-banding) unresolved: is a
  cross-map prereq valid (→ forest-validate) or a data error (→ fix 4 refs)? Decide in #260.

## Evidence
- HEAD `9160976`. `mise run verify` EXIT 0; `mise run check-maps` EXIT 0 (9 maps + synth).
- #257 subtasks: A 9f08d15, B 0b4ccdc, C 3b55f5c, D 592136e, close 56a2e11; #261 75ed752.
- ADR: `.memory/adr/0014-committed-graph-schema-minimal-overlay.md`.

## Recommended Updates
- [ ] #263: reconcile AGENTS.md "Closing a ticket" (tkt close works; stale bug claim).
- [ ] #262: visual-qa.py registers pageerror listener AFTER goto (misses load errors).
- [ ] AGENTS.md Commands (deferred): consider adding `mise run check-maps` +
      `tools/migrate_map_ids.py` rows IF a trim frees budget (at 150/150 now).
