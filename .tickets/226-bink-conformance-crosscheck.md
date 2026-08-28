---
id: "226"
title: "Verify bink reachability matches inklecate (conformance spike)"
status: done
blocked_by: []
priority: high
type: spike
tags: ["ink"]
---

# Verify bink reachability matches inklecate

## Problem

The playthrough validator (#224) uses bink (blade-ink-rs) to determine whether stories reach an ending. Research found bink's ink-spec compliance is author-attested (its own conformance suite on Inkle's canonical stories) but NOT independently verified on the public ink-proof harness. Highest risk: RANDOM/SEED_RANDOM PRNG may not match inklecate bit-for-bit.

## Why it likely doesn't matter for us (but verify)

Our validator asks a STRUCTURAL question ("does this reach END?"), not an EXACT-OUTPUT question. RNG divergence changes WHICH random branch fires, not WHETHER a story terminates. So bink should be sound for reachability even if its PRNG differs from inklecate.

This spike confirms that empirically.

## What to do

1. Pick one branching story (e.g., 02_choices_and_weave.ink)
2. Drive it through inklecate `-p` with a scripted, deterministic choice sequence (via subprocess.Popen with stdin) — record the transcript and whether it reaches "End of story"
3. Drive the SAME choice sequence through bink
4. Compare: does bink reach END where inklecate does? (Exact text may differ on RANDOM lines — that's expected and fine. Reachability verdict must match.)
5. Document the result

## Decision

- If reachability verdicts match → bink is empirically confirmed sound for our use case. Close with confidence.
- If they diverge on reachability (not just text) → investigate; may need to switch to inklecate -j subprocess backend.

## Findings (2026-08-28 — research + review subagents; see .scratch/subagent-raw/226-findings.md)

- **Windows blocker gone.** A review subagent DROVE `02_choices_and_weave.ink` through `inklecate -p`
  via `subprocess.Popen(stdin=PIPE) + communicate(timeout=20)` → exit 0, reached END, ending matched the
  golden. The #224 "stdin doesn't work on Windows" note does NOT reproduce with inklecate 1.2.1 using the
  write-all-then-read `communicate()` pattern (feed all choices up front, read to EOF; OMIT `-k`).
- **Off-by-one:** `inklecate -p` prompts `?>` and expects **1-based** choice indices; bink is **0-based**.
  Shared seq `0,0,3,1,2,2,1` (bink) → inklecate payload `1\n1\n4\n2\n3\n3\n2\n`.
- **bink is NOT in the public ink-proof conformance harness** (tests inklecate/inkjs/godot-ink/inkcpp,
  not blade-ink-rs). bink self-verifies in-repo. So our cross-check is the only LOCAL conformance
  evidence; the note will cite ink-proof (+ a `rinklecate` driver) as the broader-confidence follow-up.
- **Reuse `play_capture()` as-is** for the bink side (walks a fixed 0-based seq to END, returns transcript,
  raises InkRuntimeError on dead-end / ValueError on seq-exhausted|bad-index|turn-cap). inklecate is
  compile-only in the codebase today; both sides consume the same compiled `.ink.json`.
- **Sharper gate:** distinguish bink `InkRuntimeError` (dead end) from `ValueError: index out of range`
  (bink's CHOICE STRUCTURE diverged from the seq — a stronger conformance signal). A differing choice
  COUNT at any step is a real concern, not just a reachability mismatch.
- **Fixed seq** from `02_choices_and_weave.transcript` header: `# choices: 0,0,3,1,2,2,1` (ends "walk into the dark").
- Env: inklecate 1.2.1 (mise, PATH), Windows. Reachability (terminates y/n) is the right question because
  RANDOM/shuffle PRNG differs across C#/JS/Rust runtimes — exact text can't match cross-runtime anyway.

## Acceptance criteria

- [x] One story driven through both bink and inklecate with identical choices
- [x] Reachability verdict (reaches END or not) confirmed to match
- [x] Result documented in .memory/ (ADR or note) for future reference
- [x] If divergence found, follow-up documented

## Resolution (2026-08-28)

**Verdict: MATCH.** Drove `02_choices_and_weave.ink` through both runtimes with the committed choice
sequence `0,0,3,1,2,2,1` — bink via `play_capture()` (0-based), inklecate via `inklecate -p` +
`Popen.communicate()` with the +1 offset (1-based, no `-k`). Both reach END (exit 0, terminal text
present). Negative probe (truncated `0,0`) confirms the check discriminates: bink raises
`ValueError: choice sequence exhausted with 4 choice(s) still pending` (correct non-termination).

bink's reachability verdict is empirically sound for our use. Scope: reachability agreement on a
deterministic branching story, NOT full spec conformance (bink is not in the public ink-proof harness).
Reachability is the right question — RANDOM/shuffle PRNG differs across runtimes so exact text can't
match cross-runtime anyway.

Windows: the #224 "inklecate -p piped-stdin" concern did NOT reproduce with inklecate 1.2.1 using the
write-all-then-read `communicate()` pattern.

Verdict + method recorded in ADR 0013. Cross-check script: `.scratch/226-crosscheck.py` (throwaway
spike — not promoted to tools/). Follow-up (backlog): a `rinklecate`-based ink-proof driver for
blade-ink-rs if bink conformance ever becomes load-bearing beyond reachability.

Evidence: `.venv\Scripts\python.exe .scratch/226-crosscheck.py` → `VERDICT: MATCH ... reaches_end=True`, exit 0.
