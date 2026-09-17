---
id: "369"
title: "Root aggregate index links to gitignored workspace maps"
status: done
blocked_by: []
tags: ["ux", "generated-artifacts", "library"]
---

# Root aggregate index links to gitignored workspace maps

## Intent

A fresh clone's committed landing page must not link to files that only exist in the
gitignored live workspace.

## Context (verified 2026-09-17, UX audit + source check; also flagged by the #342 docs audit)

The committed root `lessons/index.html` (aggregate demo index, #276) bakes
`"mapHref": "../workspace/lessons/{slug}-map.html"` for domains that exist only in the
private `workspace/` — three dead links confirmed on disk:

- `../workspace/lessons/blender-godot-shaders-map.html`
- `../workspace/lessons/code-design-map.html`
- `../workspace/lessons/rust-fundamentals-map.html`

All 404 on any fresh clone (`workspace/` is gitignored). Root cause: the generator
scans the whole project root (`tools/generate_index_page.py:307-312`) and bakes
workspace-only domains into a committed artifact. Related sharp edges found while
diagnosing: `serve.py` refuses to serve the repo root at all ("Workspace has no
MAP.md files"), and `tools/assemble-site.sh` never copies root `lessons/` into
`_site/`, so this aggregate is reachable only via local static serving — worth
deciding its intended distribution as part of this fix (regenerate scanning
`library/` only, or drop workspace-only domains, or stop committing the root index).

## Acceptance criteria

- [x] Every domain link on the committed root index resolves on a fresh clone
- [x] The generator does not bake gitignored-workspace-only domains into committed output
- [x] `python tools/check-index-drift.py` (in verify) stays green; `mise run verify` exits 0

## Resolution

Root-cause fix (not output-swap): `generate_index_page.py` now filters `find_maps`
results through `git check-ignore -z --stdin` (`committed_maps_only`) before building
the domain graph, so gitignored machine-local content (the live `workspace/`) can never
be baked into a committed page, regardless of scan dir. Private `.user/` overlay maps
are unaffected (separate `find_private_maps` path, #184). Bytes + `-z` on the git call:
the Windows cp1252 locale can't encode some map filenames and git path quoting would
break matching. Root `lessons/index.html` + `library/index.html` + all 9 per-domain
indexes re-baked: the workspace-only domains (blender-godot-shaders, code-design,
rust-fundamentals, data-analytics, storage-and-table-formats) are gone; the remaining
`iceberg-workspace/` entries are the committed demo fixture, not the gitignored
workspace. `check-index-drift.py` green; full `verify` suite exits 0.
