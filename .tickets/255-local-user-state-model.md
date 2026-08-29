---
id: "255"
title: "Local user-state model: committed SR definitions, gitignored review state"
status: open
blocked_by: ["183"]
priority: high
tags: ["platform"]
---

# Local user-state model: committed SR definitions, gitignored review state

## Context

Split from #183 (ADR 0012 two-tier content model). #183 does the mechanical
rename (`examples/` → `library/`) + serve default. This ticket does the harder
half: **separate shared card definitions (committed) from per-user review state
(gitignored)**, so a fresh clone ships the library's cards but zero personal
progress, and a shared card can be updated without wiping a user's schedule.

### Current state (verified 2026-08-29, `tools/questions.py:1-31`, `tools/sm2.py`)

Today card *content* and *review state* are **coupled** in one record and one
location:

- `learning-records/questions/<topic-slug>.jsonl` — one `Card` per line.
- `learning-records/reviews.jsonl` — append-only review log.
- Both resolve **inside the workspace** (`_WORKSPACE / "learning-records"`), else
  project root.
- The `Card` dataclass (`questions.py`) bundles **content** (`prompt`,
  `expected_answer`, `question_type`, provenance, `source_quote`, …) **AND
  schedule** (`schedule: dict` = SM-2 `CardSchedule`: `interval_days`,
  `ease_factor`, `repetitions`, `due_date`, `last_reviewed`, `last_quality`) plus
  per-user flags (`suspended`, `mastered`) in the SAME JSONL line.
- `Card.id` is a random `uuid4` — NOT stable across regeneration.

The coupling means: committing the `.jsonl` commits a user's schedule; regenerating
a lesson's cards churns both content and state; two users can't share definitions
without sharing progress.

### Prior art (research 2026-08-29, `.scratch/research/multiuser-state.md`)

Anki is the canonical model: a shared deck carries only note/card **content keyed
by a stable GUID**; the user's **scheduling state + append-only revlog live
separately** and survive content updates via GUID matching on import. Universal
pattern: immutable shared content + mutable local state, **joined at runtime by a
stable content ID**, content updates **merge (not clobber)** local state. Storage
tiering: `localStorage` for prefs (already `teach-me-prefs-v1`), `IndexedDB` for
the growing SR log if state moves browser-side.

## Proposed schema

See the PROPOSED SCHEMA section below — reviewed with the owner before build.

## Design decisions to lock (before build)

1. **Where does user state physically live?** On-disk gitignored
   (`.user/state/…`, read by serve.py) OR browser (`IndexedDB`)? On-disk keeps the
   existing Python SR CLIs (`sr:review`, `sr:analytics`, `export-anki`) working;
   browser is needed for a pure static GitHub Pages deploy (no server). Likely
   BOTH, with on-disk authoritative for the served-locally workflow and an
   export/import bridge — needs an ADR.
2. **Stable card ID.** Replace `uuid4` with a deterministic slug
   (`{lesson_id}:{section}:{n}` or a content hash) so definitions match state
   across regeneration. Migration must remap existing `uuid4` ids.
3. **Merge-on-update semantics.** When a committed card's content changes but its
   ID is stable, keep the local schedule. When an ID disappears, orphan (don't
   delete) its state. When a new ID appears, it starts unseen.

## Acceptance criteria

- [ ] Card DEFINITION files (content only, stable IDs) are committed under the
      library; review STATE files are gitignored
- [ ] Fresh clone: all cards present, zero review state (nothing due, no history)
- [ ] SR CLIs (`sr:review`, `sr:status`, `sr:analytics`, `export-anki`) read the
      split model; review writes go only to the gitignored state store
- [ ] Card IDs are stable across regeneration; a migration remaps existing uuid4 ids
- [ ] Updating a committed card's content preserves the local schedule (merge by ID)
- [ ] Index/map pages read local completion state for badges (no committed progress)
- [ ] An ADR records the physical-location decision (on-disk vs browser vs both)
- [ ] `mise run verify` EXIT 0; `mise run sr` works on the split model

## Validation

Simulate a fresh clone (no state store) → `mise run sr` shows 0 due, 0 history;
review one card → state written only to gitignored store, `git status` clean of
committed progress; edit a committed card's prompt, keep its ID → schedule intact.
