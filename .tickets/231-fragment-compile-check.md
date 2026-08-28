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

## Blocker (needs a decision)

verify runs from repo root, but lesson HTML lives in gitignored
`examples/*/lessons/`. Part A can't see real lessons in CI without a committed
fixture. **Decide:** (a) commit an ink lesson HTML as a CI fixture (`git add -f`),
or (b) scope Part A to a committed fixture dir only. Until decided, Part A can't
meaningfully run in `mise run verify`.

## Also fold in

The Q15 glossary-coverage check already landed in check-lesson.py (#228). No
action needed here — noted so it isn't re-implemented.

## Acceptance criteria

- [ ] Blocker decided (committed lesson fixture vs scoped dir)
- [ ] `tools/check-lesson-code.py` extracts + compiles data-file blocks (excl. fragments)
- [ ] Diff blocks reconstructed to post-diff state before compiling
- [ ] Same-lesson fragments grouped by data-file and assembled before compile (no false undefined-divert failures)
- [ ] Only fragments with entry divert + knot decl are compiled; illustrations skipped
- [ ] Integrated into `mise run verify` with inklecate skip-guard
- [ ] Runs clean on the committed ink lesson fixture(s)
