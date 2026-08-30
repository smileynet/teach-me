---
id: "265"
title: "Windows cp1252 crash: ~21 tools print emoji/glyphs without the UTF-8 stdout guard"
status: open
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

- [ ] Every tool that prints non-ASCII to stdout/stderr has the reconfigure guard
      (grep: prints-glyphs set ⊆ guarded set)
- [ ] `mise run sr` (sr-status) runs on a cp1252 console without UnicodeEncodeError
- [ ] `mise run verify` EXIT 0 (no regression)
- [ ] Spot-check 2-3 SR tools (`sr:status`, `sr:analytics`, `quick-check`) run clean

## Validation

On a Windows console (or `PYTHONIOENCODING` unset + `chcp 1252`): run `mise run sr`,
`sr:analytics`, `quick-check`, `export_anki` — none crash with `charmap` codec errors.
