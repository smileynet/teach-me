---
id: "304"
title: "maps:regenerate task is Windows-broken (bash for-loop under cmd) — port to Python like rehydrate"
status: open
blocked_by: []
priority: low
tags: [platform, tooling, windows]
---

# maps:regenerate task is Windows-broken (bash for-loop under cmd)

## Problem

Surfaced during #301 (2026-09-05). `mise run maps:regenerate` fails immediately on Windows with
`map was unexpected at this time.` — the task body is bash (`for map in library/*/maps/*.MAP.md;
do … done`) but mise runs single-string tasks via cmd.exe on Windows, which can't parse it. This
is the SAME class of bug as the old `rehydrate` task (`mkdir -p` under cmd), which was fixed by
porting to a cross-platform Python helper (`tools/rehydrate.py`, #— see AGENTS.md).

Likely other bash-bodied tasks share the defect (audit `mise.toml` for `for`/`while`/`[ -d ]`/`$( )`).

## What to build

Port `maps:regenerate` (and any sibling bash-loop tasks) to a cross-platform Python helper, e.g.
`tools/regenerate_maps.py`: glob `library/*/maps/*.MAP.md` (+ `workspace/maps/*.MAP.md`), call the
map generator per map with the correct `--workspace`/`--output`. Point the mise task at
`uv run python tools/regenerate_maps.py`.

Note: #301 already made the generator's DEFAULT output correct, so the helper may not even need
explicit `--output` — but keep `--workspace` for the demo-status overlay rebake.

## Acceptance criteria

- [ ] `mise run maps:regenerate` runs on Windows (no cmd/bash error) and regenerates every
      committed map in place
- [ ] Cross-platform (Python, not bash); mirrors the `tools/rehydrate.py` pattern
- [ ] Audit + note any other Windows-broken bash tasks in mise.toml
- [ ] `mise run verify` EXIT 0
