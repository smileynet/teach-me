# Ink Authoring Correctness

Guidance for writing ink narrative stories and lesson code fragments that are
not just syntactically valid but produce **correct output**. The reference
stories in `ink-test-project/stories/` and the ink-godot lessons already follow
these rules — this documents the standard and the tooling that enforces it.

## The core principle

**"Compiles + reaches END" ≠ "produces correct output."** A story can compile
cleanly, pass playthrough (reach an ending), survive subagent review, and still
print the wrong text. Three bug classes (below) are invisible to structural
validation — they were caught historically only by a human reading the output.
The golden-transcript check (`mise run ink:transcripts`) is the mechanism that
catches them automatically.

## The three correctness rules

### 1. Test a knot's read count from OUTSIDE, never self-loop

A knot's read count reflects **entry**, not internal passes. A condition that
tests the enclosing knot's own count inside a self-loop never advances:

```ink
// WRONG — {shop} counts entries; self-loop never increments it
=== shop ===
{shop == 1: First visit!|Welcome back.}
+ [Look around] -> shop      // re-enters via divert, but count is stuck
```

Two correct patterns:

- **Hub-and-spoke** — divert out to a hub, re-enter the counted knot via a
  fresh divert (read count advances on each fresh entry). This is what the
  reference stories use (`well`→`village`→`well`).
- **Explicit VAR counter** — `~ visits = visits + 1` on each pass, branch on
  the variable, not the read count.

### 2. Choices in re-enterable locations must be sticky (+) or have a fallback

A once-only choice (`* [text]`) in a knot the player can re-enter (via loop-back
or tunnel) is exhausted on re-entry. Without a sticky choice or an unconditional
gather to fall through to, the player is stranded ("ran out of content"):

```ink
= weapons
* "Show me your swords." -> weapons.shown   // once-only dialogue — fine
+ [Leave] -> market_square                  // STICKY fallback — keeps loop alive
- -> market_square                          // gather also catches fall-through
```

Once-only dialogue is correct **as long as** a sticky choice or trailing gather
always gives re-entry somewhere to go.

### 3. Every code fragment must be pasteable

A lesson code block with an entry divert (`-> knot`) and a knot declaration
(`=== knot ===`) must compile on its own — no diverts to targets defined only in
prose or another block. Single-line illustrations (no entry divert) are exempt;
mark them `data-mode="fragment"`.

## Determinism (for testable output)

Stories using `{~ a|b|c}` (shuffle) or `RANDOM(min,max)` produce different output
each run. bink (the replay runtime) has **no RNG seed API**, so these stories
**cannot have a golden transcript** — the fixture would flap. The transcript tool
detects these constructs and refuses to capture them (reachability is still
covered by `mise run ink:play`). This is expected, not a gap:

- Reference stories 03 (shuffle) and 04 (`RANDOM` dice) are correctly excluded.
- Stories 01 and 02 are deterministic and have committed golden fixtures.

If you want a story's output regression-tested, keep the tested path free of
shuffle/RANDOM, or gate the randomness behind a test variable.

## The validation pipeline

| Check | Command | Catches |
|-------|---------|---------|
| Compile + lint | `mise run ink:validate` | Syntax errors, undefined diverts, warnings |
| Playthrough | `mise run ink:play` | Runtime dead-ends (never reaches END), loops |
| Golden transcript | `mise run ink:transcripts` | **Wrong output** (rules 1 & 2) on deterministic stories |
| Glossary coverage (Q15) | `tools/check-lesson.py` | Defined-but-unannotated glossary terms |

`mise run verify` runs transcript replay automatically (skips gracefully if
inklecate is absent).

## Capturing a golden transcript (reviewed artifact)

```
mise run ink:transcripts -- --story 02_choices_and_weave.ink --choices 0,0,3,1,2,2,1
```

Prints the transcript to stdout. **Read it — confirm the output is correct —
then** save it to `ink-test-project/stories/transcripts/NN_name.transcript`.

**Never blindly re-capture a fixture to make a failing diff pass.** A transcript
mismatch means either an intended change (review, then re-capture deliberately)
or a regression (fix the story). Blindly re-recording launders bugs into the
reference — the #1 documented failure mode of golden testing.
