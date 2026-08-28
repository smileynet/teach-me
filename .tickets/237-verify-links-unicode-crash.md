---
id: "237"
title: "Fix verify-links.py Unicode print crash on Windows cp1252"
status: open
blocked_by: []
priority: high
tags: ["platform"]
---

# Fix verify-links.py Unicode print crash on Windows cp1252

## Why

`mise run verify` fails on Windows even when link checking succeeds. The run
reaches the "all verified" summary (posterize-oracle passes, links resolve), then
crashes when `print()` emits `✓` / `✗` characters that the Windows cp1252 console
codec can't encode:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' ...
  File "tools/verify-links.py", line 236, in main
    print(summary)
```

This is the AGENTS.md "Python tools with Unicode stdout fail on Windows cp1252"
class. It blocks a green verify gate — we can't confidently validate any new work
(including the blender-texture-prep lessons) against a pipeline that exits 1 on a
print, not a real failure.

## Scope (revised after subagent audit — see .scratch/subagent-raw/237-code-review.md)

verify-links.py is NOT isolated. Fixing only it moves the crash one line down into
the next glyph-printing tool. A full audit of the 8 verify-pipeline tools found
**4 tools** whose non-ASCII prints (`✓ ✗ ⚠ → —`) fire on paths the verify pipeline
actually executes, and **no tool in tools/ guards stdout encoding at all**:

1. `tools/verify-links.py` — known crash; `✓` success summary (L236) + `✗`/`→`/`⚠`/`—` failure lines
2. `tools/lint-html.py` — `✗` on missing-file (L141) and per-error (L158)
3. `tools/check-svg-vars.py` — `✓` success summary (L122, ALWAYS prints), `⚠`/`—`/`✗`
4. `tools/verify-interactive.py` — report icons every run (L~330/333/336), `⚠` skip on common "playwright missing" path

Latent (not verify blockers, direct-run-only): `play-ink.py` (capture/replay of
non-ASCII story body), `test_map_parser.py` (`__main__` self-runner). Fix if cheap.
No change needed: smoke-draw-diagram.py, posterize-oracle.py, test_map_page.py.

## What to do

Add a stdout+stderr UTF-8 reconfigure block at module top of each of the 4 tools
(reconfigure chosen over glyph-swap: one line = total coverage, preserves the
project-wide `✓/✗/⚠/→` visual vocabulary, and reuses the `errors="replace"` policy
the repo already standardises on for subprocess capture — lib/ink_compile.py:94,
validate-ink-gd.py:102/117):

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

The `hasattr` guard covers Py≤3.6 and non-reconfigurable test-capture streams
(reconfigure added in 3.7 per PEP 528/540 research). Do NOT invent a shared helper
module for a 4-line guard (single-use abstraction) — inline it per tool. Do NOT
change any checking/lint/link logic — only the stdout encoding fails.

Optional belt-and-suspenders: add `env = { PYTHONIOENCODING = "utf-8" }` to
`[tasks.verify]` in mise.toml (covers all tools for mise-launched runs; does NOT
protect direct `python tools/x.py` invocation — hence per-module reconfigure is primary).

## Acceptance criteria

- [ ] `mise run verify` exits 0 on Windows (full pipeline green — verified by running it)
- [ ] verify-links.py, lint-html.py, check-svg-vars.py, verify-interactive.py each reconfigure stdout+stderr to UTF-8 at module top
- [ ] Checking/lint/link behaviour unchanged (same files checked, same failures reported on a real broken link/lint error — glyphs still render, now UTF-8)
- [ ] No regression to the other 4 verify-pipeline tools
