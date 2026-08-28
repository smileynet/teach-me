---
id: "238"
title: "Harden ink GDScript harness: deeper assertions, clean fail-test, exit-code + copy-drift fixes"
type: bug
status: done
priority: high
blocked_by: ["244"]
tags: ["ink", "validation"]
---

# Harden ink GDScript harness (#235 follow-ups)

#235 shipped a working harness that caught a real bug, but self-audit found four
weaknesses that make its "pass" less trustworthy than claimed. Close them before
relying on it to validate #236's L05 fix.

## A1 — Deepen L06 assertions
Current checks are too shallow (a wrong dispatcher could pass):
- Speaker label only checked non-empty → assert EXACT value at a known point
  (after opening, speaker == "Alfoz").
- `# sound:` dispatch never asserted → confirm the sound handler fired (capture the
  `[sound]` stdout line, or add a test-observable counter on the player).
- Suppress contract only half-tested → assert the `# hidden` line's SIDE EFFECT
  still ran (its same-line speaker tag took effect) while its text was suppressed.

## A2 — Clean deliberate-break test
The #235 prove-it-fails test accidentally introduced a PARSE error (PowerShell
mangling), so it proved "harness fails on unparseable code," not "fails on
correct-syntax-but-wrong-logic." Redo: ship a proper broken-variant file whose
`_process_tags` returns the wrong bool (compiles fine, wrong behavior), run the
harness, confirm exit 1, delete. Prove logic-bug detection, not just syntax.

## A3 — Wrapper exit-code propagation
`tools/validate-ink-gd.py` runs `--import` then the harness but ignores the import
return code — a failed import is masked. Fix: check the import subprocess result;
on import error, surface it and exit 2 (setup error). Add a note/self-check that
the wrapper's exit code equals the harness scene's exit code.

## A4 — Eliminate copy-drift
The harness runs COPIES in `ink-test-project/scenes/lesson0{5,6}_player.gd` that
were manually synced from the shipped reference files. When #236 edits the
reference, the copies silently go stale and the harness validates old code.
Fix (preferred): `validate-ink-gd.py` copies the reference files into the project
fresh on each run, so the single source of truth is the shipped reference. (Alt:
hash-check that fails loudly on drift.)

## Acceptance criteria

- [x] A1: L06 asserts exact speaker value + sound dispatch + hidden-line side-effect-ran
- [x] A2: a compiles-but-wrong-logic broken variant makes the harness exit 1 (demonstrated, then removed)
- [x] A3: wrapper exits 2 on import failure; exit code mirrors the harness
- [x] A4: harness validates the SHIPPED reference files (fresh copy or drift-check), not stale copies
- [x] `mise run ink:validate-gd` still green on correct code (after #236 fixes L05) / red on the known L05 bug before then


## Sequencing update (2026-08-28) — blocked by #244; progress so far

Reordered: #244 (mise-slim) comes FIRST because it rewrites the same wrapper. What's
already done vs deferred:
- **A1 (deeper L06 assertions): DONE** — validate_runtime.gd now asserts exact speaker
  == "Alfoz", sound command handled (returns show=true), # hidden suppressed AND
  recognized (returns show=false), ending + speaker-through-passage. Verified: L06 5/5
  green, [sound] cart_creak/cloth_unfurl/coin_drop observed in output.
- **A2 (clean logic-bug fail-test): DONE** — broke L06 `# hidden` to `show_line = true`
  (compiles, wrong logic), harness caught it with 2 assertions, exit 1, reference
  restored byte-identical. Proves logic-bug detection, not just syntax.
- **A3 (wrapper import exit-code) + A4 (copy-drift): FOLD INTO #244** — the new
  `ink-gd-run.py` (import false-exit-1 guard + exit-map) and `ink-gd-sync.py` (copy)
  ARE the A3/A4 fixes, done cleanly in the slimmed scripts rather than patched into the
  130-line wrapper. Re-verify A3 (import failure → exit 2) as part of #244's AC.

So after #244, #238's remaining scope is just confirming A3 in the new script + the
final green/red re-run. Consider closing #238 into #244 if fully absorbed.

## Resolution (2026-08-28)

All 4 ACs satisfied: A1/A2 landed here (f577090), A3/A4 absorbed by #244 (6da1ab5) + #249 (0e6ed6c). Harness asserts deep L06 behavior, catches logic bugs, guards parse errors story-text-safely, and validates the shipped reference (no drift).
