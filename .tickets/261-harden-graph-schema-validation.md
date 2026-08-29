---
id: "261"
title: "Harden #257: rename regression test + identity-first map-edge gate (related dashed, all 9 maps)"
status: done
blocked_by: []
priority: medium
tags: ["platform"]
---

# Harden #257 graph-schema validation

## Why
#257 (ULID ids + typed prereq|leads_to|related edges) is CLOSED, but four validations
were throwaway/partial (self-audit 2026-08-29). Close the gaps as committed, repeatable
gates. (Fix 4 = cross-map dangling prereqs = separate #260, NOT here.)

## Research-backed design (2026-08-29)
`.scratch/research/261-graph-render-testing.md` + `.scratch/subagent-raw/261-visualqa-fit.md`.

- **Bbox-only edge check is too weak** (my first cut): "endpoint within *some* card bbox"
  is necessary but NOT sufficient — it can't tell the CORRECT node pair from a
  plausible-wrong pair (exactly the symmetric `related` A↔B case), and flakes on
  stroke/arrowhead/DPI. Industry norm: assert against the DATA MODEL (source/target ids),
  not pixels (GLSP-Playwright, dagre edge keys, cytoscape/react-flow source/target).
- **Two-tier oracle, identity-first:**
  1. Tier 1 (exact, zero-tolerance): instrument `EdgeLayer.js` paths with
     `data-source`/`data-target`/`data-type`, `TopicCard` with `data-topic-id`. Assert
     `path[data-source=A][data-target=B]` exists once, correct type/styling, edge count
     == expected.
  2. Tier 2 (geometry, secondary): endpoints reach the two CORRECT cards via
     getPointAtLength + getScreenCTM vs getBoundingClientRect (generous tolerance now safe).
     Also the "0 detached endpoints" invariant for all 9 maps.
- **Standalone `tools/check-map-edges.py`, NOT a visual-qa focus.** visual-qa.py uses
  http.server (not serve.py) + flat lessons/ discovery; map pages need serve.py for the
  `../assets` depth-prefix (http.server → assets 404 → dagre never loads → gate FALSELY
  passes on 0 edges). New script launches `serve.py --workspace examples/{domain}` per
  workspace, .venv python (UTF-8), returns {status,metrics,errors} + exit 0/1/2.
- **Wait strategy:** NO waitForTimeout (top flake cause). MapView sets
  `data-render-complete`/`data-edge-count` after dagre layout → waitForFunction on it.
- Noted (out of scope, log only): visual-qa.py registers its `pageerror` listener AFTER
  goto (can miss load errors) — file a separate note if we touch visual-qa.

## What to build
1. **Fix 1 — rename regression test** (`test_map_parser.py`): write a fixture with a
   prereq, capture id-keyed edges, rename slug + its reference, reload, assert id-keyed
   edges byte-identical + validate clean. Pure unit test (no browser).
2. **Instrument render** (enables Tier 1): `data-source`/`data-target`/`data-type` on
   EdgeLayer paths; `data-topic-id` on TopicCard; `data-render-complete`/`data-edge-count`
   on the MapView container. Regenerate the 9 committed maps.
3. **`tools/check-map-edges.py`** (committed): loop all 9 maps — Tier-1 identity + Tier-2
   0-detached + 0 console errors; plus generate ONE synthetic soft_prereqs map and assert
   the `related` edge is dashed + no-arrow + connects the correct A↔B pair. JSON output +
   exit codes + per-map screenshot.
4. **`mise run check-maps` task** (separate from core `verify` to keep verify fast).

## Acceptance criteria
- [x] `test_map_parser.py` has a committed rename regression test (edges byte-identical
      after slug rename); passes in `mise run verify`
- [x] EdgeLayer paths carry `data-source`/`data-target`/`data-type`; TopicCard carries
      `data-topic-id`; MapView container carries `data-edge-count`/`data-render-complete`
- [x] `tools/check-map-edges.py` runs all 9 committed maps: every expected edge present
      by id+type (Tier 1), 0 detached endpoints (Tier 2), 0 console errors — exit 0
- [x] The synthetic `related` map asserts a dashed/no-arrow path connecting the correct
      pair (Tier 1 exact)
- [x] Negative tests confirm the oracle CATCHES a wrong-pair edge and a detached endpoint
      (not just green-on-happy-path)
- [x] `mise run check-maps` task added; 9 committed maps regenerated with data-* attrs

## Validation
`mise run verify` green (incl. rename test). `mise run check-maps` exit 0 across 9 maps +
the synthetic related map. Negative-test: temporarily mutate an edge's data-target to a
wrong id → gate fails (proving the oracle bites); revert.

## Resolution (2026-08-29)

Turned #257's four throwaway/partial validations into committed gates. Rename regression test locks the ULID-decoupling invariant. Identity-first two-tier map-edge oracle (data-model assertion, not bbox-only — which can't distinguish correct from plausible-wrong pairs) covers all 9 maps + a synthetic related-edge map (first render-time exercise of the dashed related path). Standalone tools/check-map-edges.py (serve.py-based, .venv UTF-8) as mise run check-maps, kept out of core verify for speed. Negative-tested to confirm it catches wrong-pair + detached defects. #260 (cross-map dangling prereqs) remains separate.
