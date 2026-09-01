---
id: "265"
title: "Windows cp1252 crash: ~21 tools print emoji/glyphs without the UTF-8 stdout guard"
status: done
blocked_by: []
tags: ["platform"]
---

# Windows cp1252 crash: ~21 tools print emoji/glyphs without the UTF-8 stdout guard

## Why

On a Windows console (default cp1252), any `print()` of a non-ASCII glyph
(✓ ✗ ⚠ → 📚 …) raises `UnicodeEncodeError: 'charmap' codec can't encode character`
and crashes the tool. Hit twice this session: `sr-status.py` (`mise run sr`) and, mid-run,
the new `migrate-add-lesson-actions.py` (fixed there by adding the guard). The whole SR
toolchain is affected, so `mise run sr` / `sr:*` crash on a fresh Windows console.

The established fix (already in ~12 tools, and in AGENTS.md Environment) is a 3-line
guard at the top of the script:

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

## Blast radius (verified 2026-08-29)

33 tools print non-ASCII glyphs; 12 already have the `stdout.reconfigure` guard → **~21
lack it**. Tools that print glyphs AND have no guard (crash on cp1252):

`sr-status.py`, `sr-lifecycle.py`, `sr-analytics.py`, `sr-check.py`, `review.py`,
`quick-check.py`, `export_anki.py`, `check-topic-completeness.py`, `check-update.py`,
`control-maps-drift.py`, `concept_hints.py`, `ingest_source.py`, `enrich_from_source.py`,
`enrich_prereqs.py`, `extract_concepts.py`, `generate_resources_page.py`,
`map_from_chunks.py`, `map_from_deps.py`, `migrate-add-breadcrumbs.py`,
`spike_ordering_comparison.py`, `spike_url_extraction.py`, `serve.py` (+ any others the
grep below surfaces).

Already guarded (reference pattern): check-lesson-code, check-map-edges, check-svg-vars,
generate_index_page, generate_map_page, lint-html, migrate-add-lesson-actions,
migrate_map_ids, serve-bg, verify-blender, verify-interactive, verify-links.

Find the gap:
```
# prints glyphs:
grep -lP 'print\(.*[\x{1F300}-\x{1FAFF}\x{2705}\x{2713}\x{2717}\x{26A0}\x{2192}]' tools/*.py
# already guarded:
grep -l 'stdout.reconfigure' tools/*.py
# gap = (prints glyphs) − (guarded)
```

## What to build

- Add the 3-line UTF-8 stdout/stderr reconfigure guard to each tool in the gap set
  (near the top, after `import sys`). Mechanical, idempotent, low-risk.
- Prefer a shared helper if it reads cleanly (e.g. `tools/lib/console.py` `force_utf8()`
  called once per script) OR just inline the guard (matches existing precedent). Inline is
  fine — it's what the 12 guarded tools already do; a helper adds an import for 3 lines.
- Do NOT change the glyphs themselves (they're fine on UTF-8 terminals; `errors="replace"`
  degrades gracefully if reconfigure is unavailable).

## Acceptance criteria

- [x] Every tool that prints non-ASCII to stdout/stderr has the reconfigure guard
      (grep: prints-glyphs set ⊆ guarded set)
- [x] `mise run sr` (sr-status) runs on a cp1252 console without UnicodeEncodeError
- [x] `mise run verify` EXIT 0 (no regression)
- [x] Spot-check 2-3 SR tools (`sr:status`, `sr:analytics`, `quick-check`) run clean

## Validation

On a Windows console (or `PYTHONIOENCODING` unset + `chcp 1252`): run `mise run sr`,
`sr:analytics`, `quick-check`, `export_anki` — none crash with `charmap` codec errors.

## Resolution

Added the UTF-8 stdout/stderr reconfigure guard to the 27-tool gap set (26 from the #265
list + `visual-qa.py`, which the original glyph-grep missed but crashed on `✓` — the bug
that surfaced this in the #283 session). 22 files took the guard right after their
`from __future__` line; 5 without a `__future__` line (`check-topic-completeness`,
`play-ink`, `test_map_parser`, `theme-preview`, `visual-qa`) took it after their docstring.

**Guard form:** self-contained `import sys as _sys` + the reconfigure block. Using `_sys`
(not `sys`) makes the guard work BEFORE the file's own `import sys` (which often comes
later) with no NameError and no shadowing. A first mechanical pass referenced bare `sys`
and crashed with `NameError` on tools whose `import sys` sat below the guard — caught by
running sr-status under cp1252, reverted, and fixed to self-import. The one-shot applier
script was removed after use (not a durable tool; inline guard matches precedent).

**Verification (cited):**
- Gap check: prints-glyph 39 ⊆ guarded 43 → GAP EMPTY.
- `PYTHONIOENCODING=cp1252`: sr-status, sr-analytics, quick-check, visual-qa all run clean
  (visual-qa prints `✓` and completes — the original crash, fixed).
- `mise run verify` EXIT 0 (exercises the guarded play-ink among others).
