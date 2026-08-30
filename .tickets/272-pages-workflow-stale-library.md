---
id: "272"
title: "GitHub Pages workflow stale: assembles nonexistent examples/, must ship library/ at consistent depth"
status: open
blocked_by: []
tags: ["platform"]
---

# GitHub Pages workflow stale: assembles nonexistent examples/, must ship library/ at consistent depth

## Why (found during #198 / ADR-0015, 2026-08-30)

`.github/workflows/pages.yml` (the #112 deploy) is stale after the `examples/`→`library/`
rename (#183) and the aggregate-index/global-map work (#198). It currently:

- Loops `for ws in examples/*/` — **`examples/` no longer exists** (renamed to `library/`).
  The glob matches nothing and `|| true` swallows the failure, so NO domain content is
  assembled into `_site/`.
- `cp docs/index.html _site/index.html` — ships a static landing page, NOT the generated
  aggregate `library/index.html` (5-domain dashboard with working `mapHref` links) or
  `library/global-map.html`.
- Lays out `_site/examples/{ws}/…` — wrong path prefix; and the pages' document-relative
  `../assets` (ADR-0015) resolves within `_site/` only if assets sit at the depth the pages
  expect. The old layout put `_site/examples/{ws}/lessons/X.html` with a per-example
  `cp -rL` of assets; the new library pages + aggregate index need a consistent layout.

Net effect: the live Pages site currently publishes only `docs/index.html` + assets — the
whole library is missing. Deploy is release-tag-gated, so it may not have visibly failed.

## What to build

- Rewrite the "Assemble deploy directory" step to assemble **`library/`** into `_site/`
  such that each page's document-relative `../assets` resolves (ADR-0015: the static
  assembly provides the unifying root, mirroring what serve.py does dynamically).
- Ship the generated aggregate landing at `_site/index.html` = the library aggregate index
  (regenerate `library/index.html` with library-root hrefs, or generate into `_site` with
  `--output _site/index.html`), plus `_site/global-map.html`. Reconcile with `docs/index.html`
  (decide: keep as landing, or replace with the aggregate index).
- Preserve: `cp -rL` for symlink resolution (Pages rejects symlinks; note the `library/*/assets`
  symlink stubs were DELETED in #198 — assets are now only at project-root `assets/`, so the
  assembly must place a copy where the pages' `../assets` reaches it), `.nojekyll`, the
  release-tag gate.
- **Base-path decision (ADR-0015):** the site deploys to a PROJECT page
  (`smileynet.github.io/teach-me/`). Document-relative paths survive a subpath IF the depth
  is consistent in `_site/` — confirm no root-relative `/assets` leaked in. Do NOT add
  `<base href>` (breaks anchors/SVG per ADR-0015) unless proven necessary.

## Acceptance criteria

- [ ] Workflow assembles `library/` (not `examples/`) into `_site/`; all domains present
- [ ] `_site/index.html` is the aggregate library index (5 domains, working card links)
- [ ] Each domain's index/map/lessons/quizzes browsable on the deployed subpath; no broken
      `../assets` links (document-relative resolves within `_site/`)
- [ ] `_site/global-map.html` present + nodes link to real domain maps
- [ ] `.nojekyll` + `cp -rL` (no symlinks) preserved; release-tag gate preserved
- [ ] Verified on the actual `/{repo}/` subpath (not just locally) — assets + nav resolve

## Validation

Run the workflow (workflow_dispatch), inspect the artifact / deployed site at
`smileynet.github.io/teach-me/`: landing shows all domains, a domain map renders with assets,
lessons load styled, back-links resolve. No `/{repo}/`-subpath 404s on `../assets`.
