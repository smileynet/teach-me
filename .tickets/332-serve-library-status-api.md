---
id: "332"
title: "Fix per-domain status API when serving library root"
status: in_progress
priority: high
blocked_by: []
type: fix
tags: ["arch-review"]
---

# Fix per-domain status API when serving the library root

## Why

The default fresh-clone serve (`mise run serve`, ADR-0012: serve the whole `library/`) renders pages for all 7 domains, but the status API works for only 1 of them. `tools/serve.py:111-114` falls back `MAPS_DIR` → `library/iceberg-workspace/maps` when the served root is `library/`:

- `/api/map/{domain}/...` 404s for every non-iceberg domain (map data is looked up in iceberg's maps dir only)
- Status POSTs and `/api/overlay` read/write `library/iceberg-workspace/.user/` regardless of domain
- Net user impact: `LessonActions.js:39,51` POST fails → "Could not save" on 6 of 7 domains in the default mode

#198 fixed this at the page level only; its API-level claim ("works with `--workspace .`") is untrue (tracked in #335). ADR-0012's "serve the whole library" is half-implemented at the API layer.

## What to build

- Resolve maps per-domain when the served root contains multiple domains: `{root}/{domain}/maps` for `/api/map/{domain}` routes, overlay rooted at the served root's `.user/`
- Keep single-workspace behavior unchanged (`--workspace library/{domain}` must behave exactly as today)
- Update the stale `serve.py:113` comment ("example workspace")

## Acceptance criteria

- [ ] `/api/map/{domain}` returns topic lists for all 7 library domains when serving `library/`
- [ ] Status POST and `/api/overlay` write to the served root's `.user/` overlay for every domain
- [ ] Playwright: serve default root → open a non-iceberg domain lesson → mark complete → reload → status persists and appears in the aggregate index's live overlay read
- [ ] Single-domain serve (`--workspace library/godot-gamedev`) regression-tested, unchanged behavior

## Resolution

TBD
