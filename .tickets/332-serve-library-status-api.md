---
id: "332"
title: "Fix per-domain status API when serving library root"
status: done
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

- [x] `/api/map/{domain}` returns topic lists for all 7 library domains when serving `library/`
- [x] Status POST and `/api/overlay` write to the served root's `.user/` overlay for every domain
- [x] Playwright: serve default root → open a non-iceberg domain lesson → mark complete → reload → status persists and appears in the aggregate index's live overlay read
- [x] Single-domain serve (`--workspace library/godot-gamedev`) regression-tested, unchanged behavior

## Resolution

Replaced the Iceberg fallback with a canonical parsed-MAP resolver. Library-root serving now scans direct domain `maps/` directories and matches the requested MAP identity exactly, which covers all 11 current map identities across seven library folders (including `data-analytics` in `iceberg-workspace` and Godot submaps). Library-root progress writes only `library/.user/status-overlay.json`; single-domain serving continues to use that domain's `.user/` overlay. Added `mise run test:status-api`, a hermetic Playwright/API fixture that exercises all map identities, completion/reload/index live-overlay behavior, and single-domain routing without touching user data. Evidence: `mise run test:status-api` → pass; direct default-root GETs returned 200 for all 11 maps; direct single-domain map and overlay GETs returned 200; `mise run verify` → pass (43 map tests, 20 interactive checks, 5 Ink transcript fixtures).
