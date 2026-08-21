---
created_at: 2026-08-20T18:59:00-07:00
base_commit: a6269b4
handoff_key: toon-shader-lessons
---

# Handoff

## Objective
Adopt proto shader lessons from gdhelper-pipeline into teach-me, establishing conventions for code block presentation, downloadable files, mechanical linting, and exercise quality — then continue generating the Godot Toon Shaders lesson track.

## Constraints
- Windows: git symlinks are text files. Use `python tools/serve.py --workspace X` (never `http.server` + junctions).
- Mise shim recursion: invoke `.venv\Scripts\python.exe` directly.
- Background servers: `Start-Process -WindowStyle Hidden`, verify via port poll.
- All lessons must pass `check-lesson.py` (11 checks) before completion.

## Prior Decisions
- Per-domain numbering (01, 02...) not global — but rename deferred to #166.
- Code blocks need `data-file`/`data-mode` attrs + downloadable files at `reference/code/{slug}/`.
- Exercises test the Win statement (core concepts), not gotchas. Research: Agarwal 2019, Wiliam 2015.
- Component abstraction: CSS-only < progressive enhancement < full Preact. No Storybook.
- Concept hints: composite scoring (depth .30, freq .20, first-appear .20, survivor .15, in-degree .15).

## Current State
- **Lessons complete:** 0001-0005 (all pass linter). Toon shader track: spatial anatomy → banding → triplanar.
- **#173 in-progress:** CSS layer done (filename labels, diff borders, fragment styling). JS CodeBlockToolbar (copy + download) remaining.
- **#181 open:** Codex review findings addressed (F1-F4 fixed), needs regression tests + fresh review.
- **Serve tool works:** `python tools/serve.py --workspace examples/godot-gamedev --lan` — no junctions.

## Next Steps
1. **#179** — Validate concept hints on real corpora (Rust, code-design, toon shaders). Quick: run script, inspect, report.
2. **#173** — Build CodeBlockToolbar.js (copy button + download link). Mount in page-shell.js.
3. **#166** — Domain subfolder scripts (rename lessons, update paths in page_template.py).
4. **Next lesson** — Outline Shaders (screen-space + mesh-extrusion toon outlines).

## Fog
- How to handle reference repos (`.references/`) for shader lessons — clone into teach-me or keep external? No decision yet.
- Ticket #139/#142 (ingest pipeline, quick quiz) closed with unchecked ACs — tracked in #159 but scope unclear.

## Evidence
- Linter: `D:\code\teach-me\.venv\Scripts\python.exe tools/check-lesson.py --workspace examples/godot-gamedev --all` → 5/5 pass
- Serve: `python tools/serve.py --workspace examples/godot-gamedev --lan` → http://192.168.0.187:8787
- Tests: 46/46 concept extraction tests pass; 161/182 total (21 pre-existing failures in enrich/ingest modules)
