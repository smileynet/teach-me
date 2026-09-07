---
id: "321"
title: "Bump pages.yml actions off deprecated Node.js 20 runner"
status: open
blocked_by: []
priority: low
validation_criteria:
  - "pages.yml uses action versions that run on Node 24 (no deprecation warning in the deploy log)"
  - "a manual workflow_dispatch deploy still succeeds end-to-end"
tags: ["platform"]
---

# Bump pages.yml actions off deprecated Node.js 20 runner

## Problem

The GitHub Pages deploy (`.github/workflows/pages.yml`) emits Node.js 20 deprecation warnings on every
run (observed on the v0.3.0 deploy, 2026-09-06):

> Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on
> Node.js 24: `actions/checkout@v4`, `actions/configure-pages@v5`, `actions/upload-pages-artifact@v4`,
> `actions/deploy-pages@v4`.

Non-blocking (the actions still run, forced onto Node 24), but it recurs every deploy and will eventually
break when GitHub drops the Node-20 shim.

## What to build

Bump the pinned action versions in `pages.yml` to releases that target Node 24 (check each action's
latest major: `actions/checkout`, `actions/configure-pages`, `actions/upload-pages-artifact`,
`actions/deploy-pages`). Keep the workflow structure (release-tag gate + workflow_dispatch) unchanged.

## Acceptance criteria

- [ ] `pages.yml` uses action versions that run on Node 24 — no Node-20 deprecation warning in the deploy log
- [ ] A manual `workflow_dispatch` deploy still succeeds end-to-end and the live site serves current content

## Notes

- Low priority — cosmetic until GitHub removes the Node-20 compatibility shim.
- Discovered during the v0.3.0 release deploy.
