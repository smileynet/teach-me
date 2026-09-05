---
id: "301"
title: "Fix: generate_map_page.py ignores workspace, writes stray root lessons/ file"
status: done
blocked_by: []
priority: high
tags: [platform, tooling]
---

# Fix: generate_map_page.py ignores workspace, writes stray root lessons/ file

## Problem

Surfaced during #253 (2026-09-04) — caused a real incident (an accidental delete/restore of a
committed map page while working around the tool). `generate_map_page.py::main()` hardcodes the
output path to `PROJECT_ROOT / "lessons" / f"{domain}-map.html"` in BOTH the `--all` loop and the
explicit-path branch. It never honors `--workspace`. Consequences:

- For any `library/{domain}` workspace, it writes a **stray** `lessons/{domain}-map.html` at the
  repo root and NEVER updates the committed map at `library/{domain}/lessons/{domain}-map.html`.
- The `mise run map:generate` task inherits this — running it appears to succeed ("✓ Generated
  lessons\\{domain}-map.html") while leaving the real committed page stale.
- Sub-maps compound it: a sub-map's committed page lives under the PARENT domain's `lessons/`, so
  even the subdirectory is wrong.

## What to build

Compute the output path from the workspace / the MAP's own location, not a hardcoded root:
- Accept `--workspace PATH` (default `PROJECT_ROOT`); default output = `workspace / "lessons" / f"{domain}-map.html"`.
- OR (more robust for sub-maps) derive from `map_path`: the committed page sits in the domain's
  `lessons/` dir, i.e. `map_path.parent.parent / "lessons" / f"{domain}-map.html"` (maps live in
  `{domain}/maps/`, pages in `{domain}/lessons/`). Pick the resolution that lands on the existing
  committed file for both top-level and sub-maps.
- Keep `--output` as an explicit override.

## Acceptance criteria

- [x] `python tools/generate_map_page.py library/godot-gamedev/maps/blender-texture-prep.MAP.md`
      (no flags) now defaults output to `library/godot-gamedev/lessons/blender-texture-prep-map.html`
      IN PLACE (no stray root file) — verified
- [x] Works for a top-level domain map AND a sub-map (both derive `{domain}/lessons/` from the
      MAP's own `{domain}/maps/` location) — verified via the resolver
- [x] No root-level `lessons/` stray created for library workspaces — verified (only pre-existing
      tracked `lessons/index.html` remains)
- [x] 41 map tests pass; generator change is behavior-preserving for content
- [ ] ~~`maps:regenerate` (all) in-place~~ → the task is Windows-broken (bash `for` loop under
      cmd.exe — same class as the rehydrate `mkdir -p` bug); could not run it end-to-end here.
      Filed as a separate follow-up. The per-map fix itself is verified via the equivalent
      `--workspace … --output …` invocation.

## Resolution (2026-09-05)

Fixed the default output path. Added `_map_output_path(map_path, domain)` — resolves the
committed page from the MAP's own location (`{domain}/maps/*.MAP.md` → `{domain}/lessons/
{domain}-map.html`), which is correct for both top-level and sub-maps. Both `main()` branches
(`--all` and explicit-path default) now use it instead of the hardcoded `PROJECT_ROOT/lessons`.

**Reframing (honest):** this is a HARDENING fix, not a critical bug. The established workflow —
`generate-topic`/`teach` skills and `.memory/specs/environment-gotchas.md` — already prescribe
the safe explicit invocation `--workspace {ws} --output {out}`, and `maps:regenerate` passes them.
My #253 incident came from running the tool WITHOUT those flags; #301 makes the bare default land
correctly too (defense-in-depth), so a future session that omits the flags no longer creates a
stray + stale committed page.

**Verified:** bare `generate_map_page.py MAP.md` now writes the committed page in place, no root
stray; 41 map tests pass. Did NOT commit any regenerated map page — a regen re-bakes demo statuses
(`in-progress`→`not-started` where no `.user` overlay reproduces them, plus css_extra template
drift from #270) which is the #278/#270 "committed maps refresh on maps:regenerate" behavior,
orthogonal to this path fix and out of scope.

**Follow-ups noted (out of scope):** (1) `maps:regenerate` is Windows-broken (bash-in-cmd) — same
fix pattern as the rehydrate Python-port. (2) regen-fidelity: regenerating a committed library map
standalone flips demo statuses; the overlay-rebake path needs the workspace's demo-status source.

## Context

- File: `tools/generate_map_page.py::main()` (~lines 420-465), `PROJECT_ROOT` at line 30.
- The AGENTS.md gotcha note (added #253) currently WARNS about this; this ticket fixes it so the
  warning can be removed.
