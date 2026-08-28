---
id: "226"
title: "Verify bink reachability matches inklecate (conformance spike)"
status: in_progress
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

## Acceptance criteria

- [ ] One story driven through both bink and inklecate with identical choices
- [ ] Reachability verdict (reaches END or not) confirmed to match
- [ ] Result documented in .memory/ (ADR or note) for future reference
- [ ] If divergence found, follow-up documented
