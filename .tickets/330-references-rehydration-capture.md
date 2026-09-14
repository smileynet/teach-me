---
id: "330"
title: "Capture .references rehydrate manifest + cross-platform rehydrate tool"
status: done
blocked_by: []
priority: low
tags: [platform, tooling, windows]
---

# Capture .references rehydrate manifest + cross-platform rehydrate tool

## What was done

Retroactive ticket (filed 2026-09-14 during a ticket-hygiene audit) for work completed on direct
instruction 2026-09-04 without a ticket. Two parts:

1. **Rehydrate manifest** — `REFERENCES.md` was stale: it listed 6 Preact/infra repos no longer on
   disk and had `git clone` lines for only 4 of the 17 actual `.references/` clones, so
   `mise run rehydrate` could not reconstruct 13 reference repos on a fresh checkout. Rewrote it
   grouped by track with an accurate `git clone` line per on-disk repo (verified 17 lines ↔ 17
   dirs); pruned the stale entries.
2. **Cross-platform rehydrate tool** — the `mise run rehydrate` task used bash-isms
   (`mkdir -p`, `while read`, `awk`, `eval`) that fail under Windows cmd.exe. Ported to
   `tools/rehydrate.py` (parse `^git clone` lines, skip existing dirs, clone the rest via argv).

## Acceptance criteria

- [x] REFERENCES.md has an accurate `git clone … .references/<dir>` line for every on-disk repo
- [x] `mise run rehydrate` runs cross-platform (Python helper, not bash) — verified on Windows
- [x] AGENTS.md documents the rehydrate contract + "record a clone line when cloning into .references/"

## Resolution (2026-09-14)

Shipped in commits `0da70b0` (docs(references): capture rehydrate info for all 17 .references
repos) and `2ad27b1` (fix(mise): cross-platform rehydrate — replace bash task with
tools/rehydrate.py). Verified at the time: `mise run rehydrate` skips all 17 existing repos
EXIT 0 on Windows; clone branch confirmed against a throwaway repo. Filed retroactively so the
work is captured as a ticket (it was done on a direct "capture rehydration info" / "fix it"
instruction). Related follow-up #304 (maps:regenerate has the same bash-in-cmd defect) remains open.
