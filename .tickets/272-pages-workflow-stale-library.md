---
id: "272"
title: "GitHub Pages workflow stale: assembles nonexistent examples/, must ship library/ at consistent depth"
status: done
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

## Chosen approach — B (nest under `_site/library/`, replicate per-domain assets) — 2026-08-30

Decided after research + code review (findings in `.scratch/research/*` and
`.scratch/subagent-raw/272-review-*.md`). Two candidates were weighed:

- **A** — flatten `library/` into `_site/` root, regenerate the two aggregate pages at
  `depth=0` so they emit bare `assets/`. Rejected: the generators ARE depth-parameterized
  (`page_template._base_page` builds `prefix = "../" * depth`), BUT `generate_index_page.py`'s
  data-island module script hardcodes `import … '../assets/components/IndexView.js'` (does not
  honor `depth`) — so A needs a code change + regenerating both aggregates, and STILL requires
  a per-domain `assets/` copy because all 70 domain pages emit `../assets` regardless. A costs
  a code change for **no reduction** in asset-copy work.
- **B — chosen.** Assemble `_site/` so the committed relative geometry resolves as-authored:

  ```
  _site/
    index.html          ← redirect: <meta http-equiv=refresh content="0; url=library/index.html">
    .nojekyll
    assets/             ← cp -rL project-root assets/  (the 2 aggregates' ../assets → here)
    library/            ← cp -rL repo library/. verbatim
      index.html, global-map.html   (../assets → _site/assets ✓)
      {domain}/
        assets/         ← cp -rL project-root assets/  (every domain page ../,../../,../../../assets → here)
        lessons/…, reference/…, maps/…
  ```

  Verified against grep of all 72 pages: only TWO physical asset locations are ever demanded —
  `_site/assets/` (the 2 aggregates) and `_site/library/{domain}/assets/` (all 70 domain-scoped
  pages, at every `../` depth). Zero page regeneration, zero code change. `mapHref` + breadcrumb
  links are already document-relative and location-independent.

Research confirmations (sources in `.scratch/research/`):
- Document-relative `../assets` SURVIVE the `/{repo}/` project-page subpath — only root-relative
  `/assets` breaks (validates ADR-0015; no `<base>`).
- The artifact must NOT be nested inside a `{repo}/` folder — Pages hosting adds the subpath, so
  `_site/` CONTENTS become the site root. (Landing at `/teach-me/` via the root redirect stub.)
- GitHub Pages rejects symlinks in the artifact → `cp -rL` (dereference) mandatory.
- `docs/index.html` is RETIRED as the landing: its card links still use the pre-rename
  `examples/` scheme and it lists only 4 of 5 domains — broken. The generated aggregate is the
  canonical landing (reached via the root redirect).

## Acceptance criteria

- [x] Workflow assembles `library/` (not `examples/`) into `_site/library/`; all 5 domains present
- [x] `_site/index.html` is a redirect stub → `library/index.html` (the 5-domain aggregate)
- [x] `_site/assets/` present (aggregates) AND `_site/library/{domain}/assets/` present for each domain
- [x] Each domain's index/map/lessons/quizzes browsable on the `/{repo}/` subpath; no broken
      `../assets` / `../../assets` / `../../../assets` links
- [x] `_site/library/global-map.html` present + nodes link to real domain maps
- [x] No root-relative `/assets` leaked in; no `<base href>` added
- [x] `.nojekyll` + `cp -rL` (no symlinks) preserved; release-tag gate preserved
- [x] Verified on a simulated `/{repo}/` subpath (not just root-served locally) — assets + nav resolve

## Verification (2026-08-30)

Reproduced the workflow assembly locally, served it under a `/teach-me/` subpath (plain
`http.server` rooted one level above a `teach-me/` dir), and ran a document-relative link
resolver over all 884 local refs in the assembled `_site`:

- **0 asset/JS/CSS/vendor misses** — every `../assets`, `../../assets`, `../../../assets`
  resolves; both aggregates hit `_site/assets/`, all domain pages hit `_site/library/{domain}/assets/`.
- **0 root-relative `/assets` refs** (ADR-0015 clean); no `<base>` added.
- Live HTTP under `/teach-me/`: root redirect, aggregate, global-map, per-domain lessons/
  quizzes/reference, deep sub-track quizzes, and vendor JS all return 200.
- Added a static analogue of serve.py's `_root_index` (redirect at each domain's
  `lessons/index.html` when absent) — resolved 17 of the breadcrumb 404s for oidc-rust +
  workout-fundamentals (which ship no per-domain lessons index).
- Excluded authoring-only asset artifacts from the deploy (`scaffolds/`,
  `workspace-template/`, `showcase.html`, `svg-patterns.md`) — 145 placeholder-link misses removed.
- `mise run verify` → EXIT 0 (verify-links 82 files, forest check, 41 unit tests, interactive
  checks, ink transcripts — all pass). `pages.yml` validates as YAML.

## Out of scope — spun off to #273

12 remaining broken nav refs are a pre-existing page-authoring defect (NOT deploy-assembly):
pages nested below `lessons/` (5 blender sub-track + iceberg `review/quick-check.html`) emit
breadcrumb links to `index.html` / `{track}-map.html` as siblings when those live one level
up. Breaks on any static host and (for the map-link) under serve.py too. Fix is in the
breadcrumb depth calc — tracked in **#273**.

## Validation

Run the workflow (workflow_dispatch), inspect the artifact / deployed site at
`smileynet.github.io/teach-me/`: landing shows all domains, a domain map renders with assets,
lessons load styled, back-links resolve. No `/{repo}/`-subpath 404s on `../assets`.


## Resolution

Rewrote the stale Pages workflow (was looping the renamed-away `examples/`) to assemble `library/`
into `_site/` (approach B): library copied verbatim under `_site/library/`, runtime assets
replicated at `_site/assets/` + each `_site/library/{domain}/assets/` so every document-relative
`../assets` resolves; root `_site/index.html` redirects to the aggregate; authoring-only asset
subdirs excluded; static analogue of serve.py's index normalizer added. Verified by assembling
`_site` locally, serving under a simulated `/teach-me/` subpath (0 asset misses, 0 root-relative),
and `mise run verify` EXIT 0. Commit b1f6f6d. Spun off #273 for a pre-existing nested-page
breadcrumb bug found during validation.
