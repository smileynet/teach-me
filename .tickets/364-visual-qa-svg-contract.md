---
id: "364"
title: "Repair the visual-QA SVG rendering failure"
status: done
priority: high
type: bug
blocked_by: []
tags: ["arch-review", "visual-qa", "curriculum"]
validation_criteria:
  - "Visual QA exercises the shipped lesson index without SVG rendering failures"
---

# Repair the visual-QA SVG rendering failure

## Intent

Repair the visual-QA failure for the shipped lessons index and make its SVG assertion diagnose the actual broken artifact.

## Context

`mise run visual-qa` currently exits 1: `lessons/index.html` has only 13 of 22 expected SVGs with non-zero dimensions. The manifest reports no JavaScript errors, so the failing rendering contract needs source-level diagnosis rather than suppression.

## What to build

Trace the index page, visual-QA selector/viewport assumptions, and generated SVG assets. Fix the responsible artifact or harness contract and retain a precise regression check.

- [x] `mise run visual-qa` exits successfully against the intended shipped library entry point — PASS: 2 checks, 0 fail against `lessons/index.html`
- [x] The failing SVG list is reported with page, selector/source, and rendered dimensions when regression occurs — failures now emit per-SVG `css path (attrs WxH, viewBox; rendered WxH; hidden-ancestor flag)` in the manifest check detail
- [x] The fix demonstrates that expected SVGs have non-zero rendered dimensions in the target viewport — manifest: "22/22 SVGs rendered (asserted across 2 view pane(s))"
- [x] The solution does not lower the expected count or ignore failed SVGs without a documented semantic reason — count stays dynamic-all (`body svg`); every SVG must render in at least one pane, and each pane's SVGs are asserted while that pane is actually visible (the toggle is exercised, not skipped). Documented semantic: UnifiedView keeps both panes mounted with display:none (#276), so "non-zero box in a hidden pane" is meaningless — the contract is per-pane visibility
- [x] Existing component interaction and JavaScript-error checks continue to run — untouched; full `mise run verify` green including `index_two_view_toggle` and the other 19 interactive checks

## Resolution (2026-09-17)

Diagnosis (reproduced + DOM-walked): the 9 "failed" SVGs all lived in UnifiedView's
inactive map pane — and behind that sat a REAL user-facing bug, not just a harness
blind spot. `GraphView`'s fit-to-view effect measured `frameRef.clientWidth` at mount;
mounted inside the `display:none` pane that is 0, so the scale factor `k` computed to
0 and the canvas was locked at `transform: scale(0)` — any learner toggling to Map on
a fresh load got an empty pane (no JS error, no re-fit on reveal). Fixes:
(1) artifact — `GraphView.js` now fits immediately when measurable and re-fits via a
ResizeObserver on the frame (pane reveal, window resize), preserving #276's
no-remount state-keeping design; (2) harness — `recipe_diagrams` in
`tools/visual-qa.py` now waits for the client-rendered view, exercises the Tree|Map
toggle, asserts each pane's SVGs while visible, and reports per-SVG selector/attrs/
rendered-dimension diagnostics on failure. Verified: `mise run visual-qa` PASS
(22/22 across 2 panes, no JS errors) and full `mise run verify` exit 0.
