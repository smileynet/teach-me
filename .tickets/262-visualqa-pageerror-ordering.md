---
id: "262"
title: "visual-qa.py registers pageerror listener after goto (can miss load-time errors)"
status: backlog
priority: medium
blocked_by: []
tags: ["platform"]
---

# visual-qa.py registers `pageerror` listener after `goto`

## Intent source
Discovered during #261 (map-edge gate) code review of `tools/visual-qa.py` — the review
flagged a listener-ordering bug adjacent to the "0 console errors" check.

## What's wrong
In `tools/visual-qa.py` `run_page()`, the `page.on("pageerror", ...)` listener is
registered AFTER `page.goto(...)` (~:238 goto, ~:243 listener). Errors thrown during the
initial load/render — before the listener attaches — are silently missed. Any check that
relies on a clean console (the no_js_errors recipe) can therefore pass on a page that
actually errored at load time.

## What to build
- Register `page.on("console", ...)` and `page.on("pageerror", ...)` BEFORE `page.goto(...)`
  so load-time errors are captured.
- Confirm the no_js_errors recipe still passes on clean pages and now FAILS on a page with
  a deliberate load-time throw (negative test).

## Context
- The new `tools/check-map-edges.py` (#261) already registers its listeners before `goto`
  — use it as the reference pattern.
- `mise run visual-qa` runs this harness.

## Acceptance criteria
- [ ] `visual-qa.py` attaches console + pageerror listeners before `goto`
- [ ] A page with a load-time JS error is reported as failing no_js_errors (add/confirm a
      negative check)
- [ ] `mise run visual-qa` still passes on the current clean pages

## Out of scope
- The port-collision issue (#241) and other visual-qa concerns.
