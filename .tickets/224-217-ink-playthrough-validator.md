---
id: "224"
title: "Ink story playthrough validator (Python JSON walker)"
status: open
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

## Implementation Plan (revised)

1. `pip install bink` into project venv (add to requirements or setup task)
2. `tools/play-ink.py`:
   - Load compiled .json (compile .ink first via inklecate if .json missing)
   - Run with bink API: `story.continue_maximally()` → get choices → choose → repeat
   - Three strategies: last-option, first-option (200-turn cap), random (200-turn cap × 3 runs)
   - Report PASS/WARN/FAIL per story
3. Add `[tasks."ink:play"]` to mise.toml
4. Integrate into verify pipeline

## Acceptance criteria

- [ ] `tools/play-ink.py` exists, stdlib-only Python
- [ ] Plays all 4 reference stories (01-04) to END with at least one strategy
- [ ] Detects intentional loops (L02 market, L04 battle) without false-failing
- [ ] Reports clearly: PASS/WARN/FAIL per story with turn count
- [ ] Integrated into `mise run ink:play` task
- [ ] Handles: text output, choices, variables, conditionals, tunnels, functions
