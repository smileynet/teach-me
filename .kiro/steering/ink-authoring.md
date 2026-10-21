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

**A third exclusion class — unbound `EXTERNAL`.** A story that declares
`EXTERNAL name(...)` with no ink `function name(...)` fallback cannot run in bink
either — bink has no external-binding API, so it errors "Missing function binding
... fallbacks disabled". `play-ink.py` detects this (`detect_unbound_externals`)
and refuses capture / skips replay, exactly like shuffle/RANDOM. Output
correctness for such a story is covered by `mise run ink:validate-gd` instead
(real Godot binds the external). Lesson 07's `07_state_bridge.ink` is the
canonical example. If you WANT a golden transcript, design the reference story
pure-ink (no unbound EXTERNAL) — lesson 08 does this and gets a real fixture.

## inkgd Phase-B runtime (lessons 05-08)

Verified against the vendored inkgd 0.6.0 (`ink_player.gd`) — the ticket paraphrases
were wrong twice, so use these signatures, not memory:

- `bind_external_function(name, object, method_name, lookahead_safe=false)` — takes
  `(object, method_name)`, **not a Callable**. Bind AFTER `create_story()`, BEFORE the
  first `continue_story()`. `lookahead_safe`: ink calls externals during choice
  lookahead, so a side-effecting external (spend gold, play sound) must be
  `lookahead_safe=false` or it fires during preview; pure functions can be `true`.
- `observe_variable(name, object, method_name)` — fires on **change**, NOT on
  registration. Seed game state once yourself right after registering
  (`_on_gold_changed("gold", get_variable("gold"))`), then the observer keeps it in sync.
  Missing this leaves a HUD blank until the first change (caught by the L07 harness).
- `get_variable(name)` / `set_variable(name, value)`; `get_state()->String` /
  `set_state(String)` — the state blob is the WHOLE story (vars + visit counts +
  callstack + seed). Never hand-save individual vars.
- The shipped player uses the single-step accumulate loop `while can_continue:
  _text += continue_story()` — append the line AS-IS (ink's line already ends in `\n`;
  adding `+ "\n"` double-spaces, the #251 bug). Never `continue_story_maximally()`
  through InkPlayer (returns only the last line — the #236 bug).

## The validation pipeline

This is the **authoritative Ink validation contract** for the project. Ink
validation is a scoped `mise` workflow — there is no `ink-validate` *skill*
(a historical ticket claimed one; it never existed — see #359). The commands
below are owned by the `mise` tasks and their backing `tools/` scripts; teaching
and generation skills link here rather than restating the operational detail.

| Check | Command | Owner | Catches | Blocks? |
|-------|---------|-------|---------|---------|
| Compile + lint | `mise run ink:validate` | `tools/validate-ink.py` | Syntax errors, undefined diverts, warnings (loose ends) | Errors fail (exit 1); warnings report but pass |
| Compile + lint (strict) | `mise run ink:validate:strict` | `tools/validate-ink.py --strict` | Same, but warnings become hard failures | Warnings fail (exit 1) |
| Playthrough | `mise run ink:play` | `tools/play-ink.py` | Runtime dead-ends (never reaches END), loops | Dead-ends fail; unbound-EXTERNAL / nondeterministic stories SKIP |
| Golden transcript | `mise run ink:transcripts` | `tools/play-ink.py --replay-transcripts` | **Wrong output** (rules 1 & 2) on deterministic stories | Mismatch fails; non-deterministic / unbound-EXTERNAL fixtures SKIP |
| Godot runtime | `mise run ink:validate-gd` | `tools/ink-gd-sync.py` + `tools/ink-gd-run.py` | Godot integration bugs bink can't see (observer timing, tag dispatch, bound EXTERNALs) | Defects fail; **SKIPs (exit 0) if Godot is absent** |
| Glossary coverage (Q15) | `tools/check-lesson.py` | `tools/check-lesson.py` | Defined-but-unannotated glossary terms | Missing annotations fail |

**Prerequisites (ADR 0013):**
- **inklecate** — provisioned by `mise` as a `[tools]` dep (`github:inkle/ink`,
  pinned in `mise.lock`), on PATH after `mise install`. Every `ink:*` task
  `depends = ["setup"]`, so a clean checkout self-provisions. Override via the
  `INKLECATE` env var. If the binary is absent, the play/transcript tools SKIP
  (exit 0) rather than hard-fail.
- **Godot** — `[env]`-only (`GODOT = { default = "godot" }`), **not** a `[tools]`
  dep (too heavy to force on every contributor). Only `ink:validate-gd` needs it,
  and that gate skips gracefully (exit 0) when Godot is missing. Override in
  gitignored `mise.local.toml`.
- **bink** — the Python replay runtime (`play-ink.py` / `ink:transcripts`),
  installed into the project `.venv` by `setup`. It has no RNG-seed or
  external-binding API, which is why shuffle/`RANDOM` and unbound-`EXTERNAL`
  stories are SKIPPED by play/transcript modes and covered by `ink:validate-gd`
  instead (see the three exclusion classes above).

**In core `verify`:** `mise run verify` runs `ink:transcripts` (transcript replay)
automatically; it skips gracefully if inklecate is absent. `ink:validate`,
`ink:play`, and `ink:validate-gd` are run explicitly (the first before closing any
Ink lesson ticket; the last before closing a Phase-B/Godot-integration ticket).

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
