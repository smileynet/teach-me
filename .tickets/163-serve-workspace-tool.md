---
id: "163"
title: "Workspace-aware serve tool with proper asset mounting"
status: done
blocked_by: []
tags: [platform]
---

# Workspace-aware serve tool with proper asset mounting

## Context

Serving lesson pages for review currently requires:
1. Knowing that `assets/` symlinks on Windows are text files (Git limitation)
2. Manually creating NTFS junctions to make the HTTP server follow them
3. Getting the serve root correct so `../assets/style.css` resolves

This is fragile and undocumented. The project needs a single command that serves any workspace correctly regardless of platform, with shared assets mounted at the right path.

Additionally, lesson numbering was wrong in the toon-shader adoption (used global 0003/0004 instead of per-domain 01/02). Per-domain numbering is the correct convention — each MAP.md domain starts from 01.

## What to build

### 1. `tools/serve-workspace.py` — workspace-aware static server

A FastAPI/Starlette script that:
- Takes `--workspace PATH` (default: `workspace/`, or first positional arg)
- Mounts `{workspace}/lessons/` at `/lessons/`
- Mounts `{workspace}/reference/` at `/reference/`
- Mounts project-root `assets/` at `/assets/` (the key fix — no symlinks needed)
- Serves on `--host 0.0.0.0 --port 8787`
- Prints available lesson URLs on startup (scan for .html files)
- Auto-opens browser with `--open` flag

### 2. Mise tasks

```toml
[tasks.serve]
run = "python tools/serve-workspace.py"
description = "Serve the default workspace"

[tasks."serve:example"]
run = "python tools/serve-workspace.py examples/$1"
description = "Serve an example workspace"

[tasks."serve:lan"]
run = "python tools/serve-workspace.py --host 0.0.0.0"
description = "Serve on LAN"
```

### 3. Fix lesson numbering (related cleanup)

Rename the adopted toon shader lessons to per-domain numbering:
- `0003-spatial-shader-anatomy.html` → `01-spatial-shader-anatomy.html`
- `0004-toon-banding.html` → `02-toon-banding.html`

Update MAP.md `lesson_file:` fields and cross-references accordingly.

### 4. Document the convention

In AGENTS.md or a steering file, state:
- Lesson numbers are **per-domain** (each MAP.md track starts from 01)
- Filename format: `NN-slug.html` (zero-padded, two digits)
- The MAP.md is authoritative for ordering within a domain
- Cross-domain references use the full path: `../other-domain/01-slug.html`

## Acceptance criteria

- [x] `mise run serve -- examples/godot-gamedev` serves lesson pages with working CSS/JS (no junctions needed)
- [x] `mise run serve` with no args serves `workspace/` if it exists, prints helpful message if not
- [x] Shared assets resolve at `/assets/` regardless of workspace location
- [x] LAN URL printed on startup (e.g., `http://192.168.x.x:8787/lessons/01-...`)
- [ ] Toon shader lessons renumbered to 01/02 (per-domain) — deferred to #166
- [x] Convention documented: per-domain numbering, NN-slug.html format
- [x] Works on Windows without symlinks/junctions (the whole point)

## Research

See `.scratch/research/` for:
- `numbering-conventions.md` — per-domain numbering is consensus best practice
- `static-serve-tooling.md` — FastAPI StaticFiles with multiple mounts is the right fit (already a dep)
- `prior-art-teaching-sites.md` — how Docusaurus/MkDocs/Hugo handle this
