---
id: "339"
title: "Use one explicit workspace context across generators and server APIs"
status: open
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

- [ ] Map generation no longer depends on process-global mutable workspace paths
- [ ] Server map and overlay lookup derive from the same context
- [ ] Explicitly selecting a workspace without maps fails clearly
- [ ] Tests prove two contexts cannot leak paths or state
- [ ] Single-domain and library-root commands remain supported
- [ ] `mise run verify` exits 0

## Resolution

TBD
