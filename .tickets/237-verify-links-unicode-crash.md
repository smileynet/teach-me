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

## Scope

`tools/verify-links.py` — lines ~228 and ~237 (the `✓ All links verified` and
`✗ N broken link(s)` summary prints).

Sweep for the same pattern in sibling verify-pipeline tools if trivially adjacent
(e.g. any other tool `mise run verify` invokes that prints non-ASCII), but the
crashing tool is verify-links.py.

## What to do

Make stdout UTF-8 safe on Windows. Pick the least-invasive fix that matches
existing project convention (AGENTS.md suggests `set PYTHONIOENCODING=utf-8` or
avoiding non-ASCII in `print()`):

- Preferred: reconfigure stdout to UTF-8 at startup
  (`sys.stdout.reconfigure(encoding="utf-8")`, guarded for older interpreters), OR
- Replace the `✓`/`✗` glyphs with ASCII markers (`[OK]` / `[FAIL]`) consistent
  with other project tool output.

Do NOT change link-checking logic — the check itself passes; only the print fails.

## Acceptance criteria

- [ ] `mise run verify` exits 0 on Windows (full pipeline green, not just links)
- [ ] verify-links.py prints its success/failure summary without UnicodeEncodeError
- [ ] Link-checking behaviour unchanged (same files checked, same failures reported on a real broken link)
- [ ] No regression to other verify-pipeline tools
