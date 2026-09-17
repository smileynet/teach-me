---
id: "342"
title: "Reconcile governing architecture documents with the shipped system"
status: done
priority: high
blocked_by: ["335"]
type: docs
tags: ["arch-review", "platform"]
validation_criteria:
  - "ui-contracts.md describes page-shell.js as implemented"
  - "map-format-spec.md documents ULIDs, typed edges, and no committed learner status"
  - "ADR 0014 and README describe the reconciled shared-library/local-state architecture"
---

# Reconcile governing architecture documents with the shipped system

## Problem

The UI spec calls `page-shell.js` unimplemented, the MAP spec embeds learner status and omits
the ULID/typed-edge schema, ADR 0014 remains proposed after implementation, and README blurs
the committed library with local workspace/state.

## Context

Read `.memory/specs/ui-contracts.md`, `.memory/map-format-spec.md`, ADRs 0012/0014/0016,
`README.md`, and #335. Reconcile ticket records first so docs cite honest as-built evidence.

## What to build

Establish one current description of committed shared content, immutable graph identity,
typed relationships, the implemented page shell, and local-only learner state.

## Acceptance criteria

- [x] UI contracts describe the implemented page-shell interface — ui-contracts.md section rewritten: ordered imperative init + extension contract + page_template.py as the server-side twin (was "not yet implemented, ticket 127")
- [x] MAP format matches `map_parser.py` for IDs, edges, prerequisites, and state exclusion — map-format-spec.md rewritten as-built: ULID `id` field, EDGE_TYPES + `## Edges` block, `scope`/`soft_prereqs`/`aliases`/`lesson_file`, status removed (overlay rule), cross-map prereq resolution, leads_to's three authoring forms, max-9-validated rule; also fixed `resolve_map_filename`'s docstring to match its body
- [x] ADR 0014 status is reconciled with an as-built note — flipped to accepted with three recorded deviations (SR keying by card UUID not node id; topic-level leads_to in-file only; §B.6 partially superseded by ADR-0018 for SR events)
- [x] README distinguishes library, workspace, `.user` state, and demo fixtures — new "Where things live" table; serve behavior corrected; "Example Workspaces" renamed to "Public Topic Library" with all seven workspaces
- [x] No current document instructs users to commit learner progress — the map-format-spec was the last offender (status template + Rule 8); rewritten. Skills' guidance verified correct
- [x] Links resolve and `mise run verify` exits 0 — full verify run 2026-09-17: all gates green (links, lint, lesson code compile, SVG vars, map tests, 20 interactive checks, ink replay), 76.9s

## Resolution (2026-09-17)

Reconciled every governing document with the shipped system, working from a subagent
docs↔code mismatch inventory with every item evidenced at file:line, then applied and
gated: `.memory/specs/ui-contracts.md` (page-shell as implemented), `.memory/map-format-spec.md`
(full as-built rewrite — the central drift: committed `status` field no longer exists,
ULIDs + typed edges do), ADR 0014 (accepted + as-built deviations), ADR 0016 (#284
limitation resolved, #279 follow-up corrected), README ("Where things live" + library
framing), CONTRIBUTING (`examples/` → `library/`), AGENTS.md (workspace auto-create
phrasing, nonexistent `assets/services/` row removed, preact_page.py marked deprecated
duplicate, Test Fixture section points at `library/iceberg-workspace/` with demo-vs-
learner-data distinction). `mise run verify` exits 0. Follow-ups surfaced but NOT done
here (out of scope): the committed root `lessons/index.html` bakes gitignored-workspace
references into `mapHref` (generate_index_page whole-root scan) — worth its own ticket.
