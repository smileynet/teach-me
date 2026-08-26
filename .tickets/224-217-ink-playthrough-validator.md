---
id: "224"
title: "Ink story playthrough validator (Python JSON walker)"
status: done
blocked_by: []
priority: high
type: feature
tags: ["ink"]
---

# Ink story playthrough validator (Python JSON walker)

## Problem

Reference stories compile clean but we can't verify they actually play to completion. Stories with loops (L02 market, L04 battle) could hang if choices are made in certain orders. inklecate -p doesn't work with piped input on Windows. No automated playthrough validation exists.

## What to build

`tools/play-ink.py` — a minimal Python ink JSON runtime that:

1. Loads a compiled .json story (from inklecate -o)
2. Runs the story with an automated choice strategy
3. Reports: reached END (pass), hung at turn N (fail), or errored (fail)

### Choice strategies (run in order, any passing = story PASS):

1. **Last option** — always pick the last choice (most likely "leave"/"flee"/"END")
2. **First option** — always pick choice 1, 200-turn cap (detects unintentional infinite loops)
3. **Random** — random choices, 200-turn cap, 3 attempts

### Decision logic:
- Strategy 1 reaches END → PASS (story has a reachable exit via last options)
- Strategy 1 AND 2 both hang → WARN (may be intentional loop without auto-exit)
- No strategy reaches END in any run → FAIL

### Integration:
- `mise run ink:play` — run all reference stories through the validator
- Part of `mise run verify` pipeline
- Compile .ink → .json automatically before playing

## Research Findings (2026-08-26)

### Existing Python ink runtimes
- **bink** (pip install bink, v0.7.1, Apache 2.0) — Rust-based, full ink spec, pre-built wheels for all platforms. RECOMMENDED.
- inkpython (v0.1, pure Python port of inkjs) — too early/incomplete
- inkpy (archived), InkPython (hobby/broken), inkcpp-python (needs binary compilation)

### Building from scratch: NOT recommended
- Full ink runtime is 8-10K LOC (stack-based VM with evaluation stack, callstack, visit counting, native functions)
- Minimal subset for choice-only play still ~500-1000 lines, would miss edge cases
- bink gives full compliance for zero effort

### Alternative: inklecate subprocess
- Can redirect stdin/stdout via PowerShell Start-Process
- Fragile on Windows but works as fallback
- Already proven in validate-ink.py (subprocess pattern)

## Implementation Plan (finalized 2026-08-26)

### Backend: bink (verified working)
- Correct import is `from bink.story import Story, story_from_file` (NOT `import bink`, which only exposes constants)
- Clean OOP API hides all FFI/memory management: `can_continue()`, `cont()`, `choices`, `choose_choice_index(i)`
- Verified end-to-end: loaded L02 compiled story, continued through text, got choices as plain strings
- Requires compiled .ink.json (compile via inklecate first)

### Why bink over inklecate -p subprocess
- Clean in-process API vs parsing line-delimited JSON from `-p -j` + process lifecycle management
- Full spec (variables, visit counts, tunnels, functions)
- inklecate -p -j is the documented fallback if bink breaks

### tools/play-ink.py
1. Find .ink files in ink-test-project/stories/ (reuse DEFAULT_INK_DIR, DEFAULT_INKLECATE)
2. Compile each to .ink.json (reuse validate-ink.py subprocess pattern)
3. Load with bink, run 3 strategies (fresh instance each):
   - LAST: pick last choice, 200-turn cap
   - FIRST: pick choice[0], 200-turn cap
   - RANDOM: random choice, 3 runs, 200-turn cap
4. Classify: any strategy reaches END → PASS; loops without ending → note; exception → FAIL
5. Report PASS/WARN/FAIL per story + turn counts
6. Exit codes: 0=pass, 1=fail, 2=setup error

### Prior art alignment
Matches Ink-Tester Monte Carlo pattern. No tool proves "all paths reach END" (known white space). 3-strategy approach is the pragmatic standard.

## Acceptance criteria

- [x] `tools/play-ink.py` exists, uses bink (added to setup task's uv pip install)
- [x] Plays all reference stories (01-04 + hello) to END with at least one strategy
- [x] Detects intentional loops (L02 market, L04 battle) without false-failing
- [x] Reports clearly: PASS/WARN/FAIL per story with turn count
- [x] Integrated into `mise run ink:play` task (depends=["setup"])
- [x] Handles: text output, choices, variables, conditionals, tunnels, functions

## Resolution (2026-08-26)

Built `tools/play-ink.py` (187 lines) using bink. The validator immediately earned its keep — it found REAL runtime dead-ends in stories 02 and 04 that compile-time validation (`--strict`) missed:

- **Root cause:** once-only choices (`*`) in locations that are revisited (sticky-loop hubs, tunnels called multiple times). When all choices in a group deplete and there's no fallback, ink errors with "ran out of content" — but only at runtime on that specific path.
- **Fix:** made choices sticky (`+`) or added sticky fallbacks (`+ ->`) in: L02 market stitches + tavern groups; L04 battle/camp choices + forest/cave hubs.
- Both HTML complete-story blocks synced with the fixed .ink files.

Final: all 5 stories PASS playthrough AND strict compile. check-lesson passes L02 (10) and L04 (9).
