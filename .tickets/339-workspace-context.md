---
id: "339"
title: "Use one explicit workspace context across generators and server APIs"
status: done
priority: high
blocked_by: ["332"]
type: refactor
tags: ["arch-review", "platform"]
validation_criteria:
  - "Two workspaces run in one process without cross-workspace reads or writes"
  - "An invalid explicit workspace fails instead of falling back to a fixture"
  - "mise run verify exits 0"
---

# Use one explicit workspace context across generators and server APIs

## Problem

The review found mutable workspace globals in `generate_map_page.py` and a silent Iceberg
fallback in `serve.py`. These can combine content from one root with state from another.

## Context

Read `tools/generate_map_page.py`, `tools/serve.py`, `tools/lib/domain_graph.py`,
`tools/lib/overlay.py`, ADR 0012, and ADR 0015. Build on #332's multi-domain resolver.

## What to build

Represent content root, maps, lessons, questions, and local overlay root as one explicit
context. Default-library selection occurs only at the CLI entry point when no workspace was
selected; malformed explicit workspaces fail clearly.

## Acceptance criteria

- [x] Map generation no longer depends on process-global mutable workspace paths
- [x] Server map and overlay lookup derive from the same context
- [x] Explicitly selecting a workspace without maps fails clearly
- [x] Tests prove two contexts cannot leak paths or state
- [x] Single-domain and library-root commands remain supported
- [x] `mise run verify` exits 0

## Resolution

Added immutable `WorkspaceContext`, which validates one selected root and carries its map
files, lessons directory, question directory, local overlay root, and single-vs-multi-domain
mode. `serve.py` now resolves maps and opens the overlay exclusively through that context;
the old Iceberg `MAPS_DIR` fallback is removed. `generate_map_page.py` passes an explicit
context through output, lesson discovery, and page generation instead of mutating module
globals. Its `--workspace` option now rejects a selected root with no MAP.md files and
rejects maps outside the selected context.

`test_workspace_context.py` proves independent workspaces do not share content paths or
overlay state, that map generation reads only its supplied context, and that an invalid
explicit server selection fails clearly. It is included in core `mise run verify`.

Evidence: `python tools/test-library-status-api.py` → library-root plus single-domain local
progress flow passes across 11 map identities; `python tools/check-map-edges.py` → 12 maps,
0 failures or detached edges; `mise run verify` → 47 tests, 20 interactive checks, and 5 Ink
transcript replays pass (83.74s).
