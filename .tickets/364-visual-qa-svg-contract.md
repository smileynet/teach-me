---
id: "364"
title: "Repair the visual-QA SVG rendering failure"
status: open
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

- [ ] `mise run visual-qa` exits successfully against the intended shipped library entry point.
- [ ] The failing SVG list is reported with page, selector/source, and rendered dimensions when regression occurs.
- [ ] The fix demonstrates that expected SVGs have non-zero rendered dimensions in the target viewport.
- [ ] The solution does not lower the expected count or ignore failed SVGs without a documented semantic reason.
- [ ] Existing component interaction and JavaScript-error checks continue to run.
