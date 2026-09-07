---
id: "321"
title: "Bump pages.yml actions off deprecated Node.js 20 runner"
status: done
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

- [x] `pages.yml` uses action versions that run on Node 24 — no Node-20 deprecation warning in the deploy log
- [x] A manual `workflow_dispatch` deploy still succeeds end-to-end and the live site serves current content

## Notes

- Low priority — cosmetic until GitHub removes the Node-20 compatibility shim.
- Discovered during the v0.3.0 release deploy.

## Resolution

Bumped all four Pages-deploy actions in `.github/workflows/pages.yml` to their Node-24 majors:
`actions/checkout` @v4→@v5 (both check-tag + build jobs), `actions/configure-pages` @v5→@v6,
`actions/upload-pages-artifact` @v4→@v5, `actions/deploy-pages` @v4→@v5. Versions verified against each
action's `action.yml runs.using` (`.scratch/research/321-action-versions.md`).

No `with:`-input changes needed (`fetch-depth`/`enablement`/`path` are stable core inputs); the
upload-artifact immutable/hidden-files break predates this bump (already in the v4 baseline, per
`.scratch/research/321-action-pinning.md`). Kept major-tag pinning (repo convention; first-party actions,
secret-less public deploy — SHA-pinning noted as an optional future policy, not adopted). Control plane
unchanged: `on:[push main + workflow_dispatch]`, release-tag gate, `assemble-site.sh` step, no tag trigger.
Single-file change (pages.yml is the only workflow).

**Verified via a live manual `workflow_dispatch` run (34121148041):**
- All 3 jobs passed (check-tag ✓, build ✓, deploy ✓).
- The Node.js 20 deprecation warnings are GONE from the log (the only remaining "deprecated" line is an
  unrelated Node-24-internal `punycode` DeprecationWarning — not a runner/action deprecation, not ours).
- Live site still serves current content (root, aggregate index, gltf-format lesson 06 all 200).

Committed 550d053.
