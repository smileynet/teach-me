---
id: "231"
title: "Fragment-compile validation for lesson code blocks (#228 Part A)"
type: feature
status: in_progress
priority: high
blocked_by: []
tags: ["ink", "validation"]
---

# Fragment-compile validation for lesson code blocks (#228 Part A)

Deferred from #228. Parts B (golden transcripts), C/D (audits), Q15 (glossary
coverage), and the meta-lesson steering all landed there. Part A was deferred
because it has an unresolved blocker (below).

## What to build

Extract every `<pre data-file ...><code>` block from lesson HTML (excluding
`data-mode="fragment"` illustrations), decode HTML entities, reconstruct the
post-diff state for `data-mode="diff"` blocks, and compile with inklecate.
FAIL on any fragment that has a `-> ` entry divert + a `=== knot ===`
declaration but doesn't compile. This catches bug class #1 (diverts to
undefined knots — a fragment that won't compile if the reader pastes it).

## Reuse (already in place from #228)

- `tools/lib/ink_compile.py` — `compile_source(str)` compiles ink from a string
  (built exactly for this). Also `ISSUE_PATTERN`, `inklecate_available`.
- `tools/check-lesson.py::check_g3_code_files` (line ~66) — the `data-file`
  extraction regex that already excludes `data-mode="fragment"`.
- Recommendation from #228 review: NEW tool `tools/check-lesson-code.py`, not
  check-lesson.py (which is deliberately compiler-free). Wire into verify.

## The two hard parts (flagged in #228 review)

1. **Diff-fragment reconstruction** — `data-mode="diff"` blocks contain `-`
   (removed) and `+` (added) lines wrapped in `<span style="color:var(--error)">`
   / `--success`. To compile the post-diff state: strip removed lines, unwrap
   spans, `html.unescape`. No prior art in the repo.
2. **Fragment self-containment** — fragments legitimately reference knots defined
   in OTHER blocks of the same lesson. Compiling each in isolation → false
   "undefined divert" failures. Fix: group blocks by `data-file` value, assemble
   in document order, compile the assembled file (matches how the reader
   downloads the final file).

## Blocker — RESOLVED (2026-08-28)

Moot. Lesson HTML is **tracked**, not gitignored — the #234 anchored-gitignore fix made only top-level
`/workspace/` ignored; `examples/*/lessons/` are committed fixtures (`git check-ignore` returns not-ignored;
8 ink lesson files in `git ls-files`). No fixture decision needed. The gate runs over the real committed corpus.

## Scope — Option A (language-aware), chosen 2026-08-28

The `data-file` extractable content is cross-language, so a pure-ink gate would compile nothing in the ink
lessons (their only `.ink` data-file block is `fragment`). Build a language-aware gate keyed by extension:
- `.ink` → inklecate (`ink_compile.compile_source`) — a FORWARD guard for lessons 07/08 (complete-mode .ink)
- `.py`  → `python -m py_compile` (blender-texture-prep) — no skip-guard (Python always present)
- `.gd`/`.gdshader` → Godot headless import (godot-gamedev + ink story_player.gd) — skip-guarded

## Findings (research + review subagents; see .scratch/subagent-raw/231-findings.md)
- Extraction: DON'T reuse `check_g3_code_files` (filename-only, existence dicts). Reuse only its
  fragment-exclusion idiom; write a NEW DOTALL regex capturing the `<pre>` tag + `<code>` body.
- Diff reconstruct (only 3 files, all `.gdshader`: 0004, 0006, showcase): UNWRAP `--success`/`--error`
  spans FIRST (they straddle newlines), THEN classify each line by first char; `html.unescape` once, last.
  Drop `-` lines, keep context/`+` (strip 1-char gutter). Compile the ASSEMBLED file (grouped by data-file).
- Skip-guards: `.ink` via `inklecate_available()` → SKIP exit 0 (do NOT copy validate-ink.py's exit-2).
  Godot via `resolve_godot()` (GODOT env → which → SKIP). Godot headless import returns exit 0 EVEN ON
  parse errors → scan stdout for `SCRIPT ERROR`/`ERROR: Failed to load script`, never trust exit code.
- Windows: inline UTF-8 stdout+stderr reconfigure at module top; wire as ONE `uv run python ...` string
  in the `[tasks.verify]` ARRAY.

## Acceptance criteria

- [x] `tools/check-lesson-code.py` extracts non-fragment `data-file` blocks (new DOTALL body regex; fragment-excluded)
- [x] Blocks grouped by `data-file` and assembled in document order before compile (no false cross-block failures)
- [x] Diff blocks reconstructed to post-diff state (unwrap-spans-first, unescape-once) before compile
- [x] Language dispatch by extension: `.ink`→inklecate, `.py`→py_compile; `.gd`/`.gdshader`→SKIP (opt-in Godot, see resolution)
- [x] Per-language graceful skip-guards (`.ink` inklecate_available → SKIP exit 0; `.gd`/`.gdshader` SKIP)
- [x] Integrated into `mise run verify` (array entry); Windows UTF-8 stdout guard inlined
- [x] Runs clean on the committed corpus; mutation-verified (break a divert → fail; restore → green)

## Resolution (2026-08-28) — Option A (language-aware)

Built `tools/check-lesson-code.py`: extracts non-fragment `data-file` blocks (new DOTALL `<pre>…<code>`
regex reusing only the fragment-exclusion idiom), groups by `data-file` and assembles in document order,
reconstructs `data-mode="diff"` blocks to post-diff state (unwrap `--success`/`--error` spans FIRST since
they straddle newlines, then classify by first char, `html.unescape` once), and dispatches by extension.
Wired into `mise run verify` (array entry) + AGENTS.md Commands row.

**Coverage:** `5 compiled, 22 skipped, 0 failed` on the committed corpus.
- `.ink` → inklecate (`compile_source`), skip-guarded via `inklecate_available()`. Compiles the 4
  reference stories' `complete`-mode blocks (01–04) TODAY (better than predicted — the lessons DO have
  `complete` .ink blocks alongside the excluded `fragment` ones) + forward-guards lessons 07/08.
- `.py` → `python -m py_compile` (no guard; Python always present). Compiles `posterize_rgb.py`.
- `.gd`/`.gdshader` → **SKIP (opt-in)**. Scope decision: a full Godot headless import harness (write
  extracted file into the right project, import, scan for `SCRIPT ERROR` since headless returns 0 even
  on parse errors) is disproportionate for this ticket and would put Godot in core verify. Reported as
  an honest SKIP with a reason string; the Godot compile-check remains manual/opt-in (matches the
  mktoon visual-gate posture). Follow-up if wanted: a `check-lesson-code.py --godot` mode that reuses
  ink-gd-run.py's resolve_godot + parse-error scan against test-scene/ink-test-project.

**Mutation-verified:** injected an undefined divert (`-> mutation_undefined_knot_251`) into lesson 02's
`complete` .ink block → gate FAILED with `L6: Divert target not found` (exit 1); restored → green.
Diff reconstruction verified by dumping the `0004-toon-banding.html` diff block → correct post-diff
`toon_smoothstep.gdshader` (removed `step()` line dropped, both added lines + smoothstep kept, gutters
stripped).

Evidence: `mise run verify` EXIT 0 (`check-lesson-code: 5 compiled, 22 skipped, 0 failed`).
