---
id: "280"
title: "Local _site deploy assembly dry-run (verify subpath + overlay survival)"
status: done
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

- [x] `_site` assembly script runs locally without error
- [x] Unified page, redirect stub, and demo overlays all present + correct
- [x] Document-relative asset paths from the aggregate + domain lesson pages resolve
- [x] Root redirect works
- [x] `mise run verify` EXIT 0 (unchanged)

## Resolution

Went beyond a one-shot dry-run: **extracted the `_site` assembly into a single-source script**
`tools/assemble-site.sh` (Option B — the "Uniform Build" pattern; research-backed). `pages.yml`
now calls `bash tools/assemble-site.sh _site` (control plane in YAML, assembly logic in the
script), and `tools/site-dry-run.py` runs that SAME script into a temp dir — so the dry-run
exercises the EXACT deploy logic, no re-implementation to drift.

**Reconciled the stale (pre-#279/#281) ticket expectations:**
- The ticket's ".user survived the strip" AC was INVERTED by #279 — the dry-run now asserts
  the opposite (correctly): `demo-status.json` fixtures ship (3), NO `.user/` anywhere.
- #281 made all 5 per-domain indexes exist → the missing-index redirect loop is dormant; the
  dry-run asserts 0 stubs written + all 5 indexes present.
- **Fixed a latent bug** the review found: the missing-index redirect target lacked `../` to
  escape `lessons/` (would 404 for a future index-less domain). Now `../{domain}-map.html`.

`tools/site-dry-run.py` (mise task `site-dry-run`, NOT core verify — needs git-bash) asserts
12 invariants: root redirect, `.nojekyll`, shared + per-domain assets, aggregate + global-map,
5 per-domain indexes, 0 stubs, 3 demo fixtures, no `.user/`, **no root-relative `/assets`
refs** (the ADR-0015 subpath invariant — which verify-links does NOT enforce, per review), no
symlinks, and the `../` redirect fix.

ADR 0015 amended (the assembler is the single source of the document-relative invariant; the
dry-run enforces it pre-release, not only on a `v*` tag).

**Verification:** `mise run site-dry-run` → 12/12 assertions pass; `mise run verify` EXIT 0
(unchanged — one flaky 3-check timeout during a 253s run, confirmed transient by a clean 71s
re-run; my changes don't touch verify-interactive). Extracted script validated byte-faithful
via git-bash (5 per-domain indexes, 3 demo fixtures, 0 `.user/`, assets at root + 5 domains).

## References
- `.github/workflows/pages.yml` — the "Assemble deploy directory" step (the shell block to run
  locally); `copy_assets()` helper, `cp -rL library/. _site/library/`, the per-domain assets +
  missing-index loops, the root redirect heredoc, and the `rm -rf _site/.user` strip (scoped by #278).
- ADR 0015 (`.memory/adr/0015-unifying-root-document-relative-assets.md`) — the document-relative
  `../assets` invariant this dry-run confirms on the `/{repo}/` subpath.
- #278 resolution (`.tickets/278-*.md`) — why only `_site/.user` (not `_site/library/.user`) is stripped.
- serve.py `/{domain}/...` path convention (AGENTS.md Env) — how the same pages resolve when served locally.
