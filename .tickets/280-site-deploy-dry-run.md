---
id: "280"
title: "Local _site deploy assembly dry-run (verify subpath + overlay survival)"
status: open
blocked_by: []
tags: [platform]
---

# Local _site deploy assembly dry-run (verify subpath + overlay survival)

## Context

#276 (unified two-view page) and #278 (committed demo overlay) changed what ships in
`library/` — a new `library/index.html` (UnifiedView), a redirect stub `global-map.html`,
and committed `.user/status-overlay.json` per domain. The deploy assembly in
`.github/workflows/pages.yml` copies `library/**` verbatim via `cp -rL` and then strips
private overlays. #276 verified document-relative paths locally + verify-links, but the
**actual `_site` assembly + GitHub Pages `/{repo}/` subpath** was not exercised (deploy only
fires on a `v*` tag).

## What to do

Run the `pages.yml` assemble-step logic locally (the shell block, minus the upload):

1. `mkdir _site`
2. `copy_assets _site/assets/`
3. `cp -rL library/. _site/library/`
4. Per-domain assets loop
5. Missing-index redirect stubs
6. Root redirect → `_site/index.html`
7. Strip: `rm -rf _site/.user` (NOT `_site/library/.user` — per #278)
8. `.nojekyll`

Then verify:
- `_site/library/index.html` has the unified page (UnifiedView in the module script)
- `_site/library/global-map.html` is the redirect stub
- `_site/library/{ink-godot,godot-gamedev,iceberg-workspace}/.user/status-overlay.json` survived the strip
- `../assets` from `library/index.html` resolves to `_site/assets/`
- A lesson page's `../../assets` resolves correctly
- `_site/index.html` redirects to `library/index.html`

## Acceptance criteria

- [ ] `_site` assembly script runs locally without error
- [ ] Unified page, redirect stub, and demo overlays all present + correct
- [ ] Document-relative asset paths from the aggregate + domain lesson pages resolve
- [ ] Root redirect works
- [ ] `mise run verify` EXIT 0 (unchanged)
