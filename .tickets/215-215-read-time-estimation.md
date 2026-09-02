---
id: "215"
title: "Read-time estimation tooling"
status: done
blocked_by: []
priority: high
type: feature
tags: [platform]
---

# Read-time estimation tooling

## Problem

Lessons declare a read time in `lesson-meta` (e.g., "~12 min read") but this is set manually with no calculation behind it. There's no tool to compute it from lesson content, and no validated formula for technical content with code blocks.

Current state: `page_template.py` accepts `reading_time` as a manual integer parameter. No automated word-count or time estimation exists.

## What to research (via subagents)

1. **Formula validation** — use existing lessons (01: ~8 min, 02: ~12 min) as calibration points. Count prose words, code characters, and images. Determine what WPM + code penalty produces those stated times.
2. **Industry approaches** — Medium (265 WPM, no code handling), ngryman/reading-time (200 WPM flat), Bomberbot (4ms/char for code), Grigora (30s/block flat). Which fits our content?
3. **Teaching-specific considerations** — learners read slower than experts. Should we use a "beginner technical" rate (~150 WPM) rather than a general rate (~200 WPM)?
4. **Code block treatment** — flat penalty per block (30-60s), character-based (4ms/char), or WPM at reduced rate? Our code blocks range from 3-line snippets to 90-line reference stories.

## Proposed deliverable

`tools/estimate-read-time.py` — stdlib Python script that:
- Parses lesson HTML, strips tags
- Counts prose words (excluding code blocks, glossary JSON, nav, scripts)
- Counts code block content separately (characters or lines)
- Applies formula: `ceil(prose_words / WPM + code_penalty)`
- Outputs the estimated read time
- Optionally updates the lesson-meta div in-place

Integration: `check-lesson.py` warns if stated time differs from estimate by >30%.

## Acceptance criteria

- [x] Research complete: formula validated against lessons 01 + 02 as calibration
- [x] `tools/estimate-read-time.py` exists, stdlib-only
- [x] Running on lesson 01 produces ~8 min; on lesson 02 produces ~12 min (±2 min)
- [x] Integrated with `check-lesson.py` as a warning (not blocking)
- [x] Formula documented in a comment or README

## Resolution (2026-09-02)

**Formula (empirically calibrated, stdlib-only):**
`minutes = ceil(prose_words / 200 + code_lines * 1.5 / 60)`
- 200 WPM prose (ngryman/reading-time default; a slower "beginner" rate over-counted both anchors)
- 1.5 s per non-blank code line (per-LINE penalty tracks scan effort better than per-char or flat-per-block)
- ceil (a partial minute still costs a minute)

Derived by measuring the two anchor lessons and fitting round, citable constants (not an
overfit 2-point exact solve). Calibration anchors are the ink-godot track (the only 8/12
pair): `0001-ink-flow-and-knots` (1090 words, 86 non-blank code lines) → **8 min** (declared
~8, exact); `0002-ink-choices-and-weave` (1272 words, 195 lines) → **12 min** (declared ~12,
exact). Both dead-on, well inside ±2.

**Deliverable:** `tools/estimate-read-time.py` — stdlib `html.parser`, importable
(`estimate_read_time`, `declared_read_time`, `update_read_time`, `measure`) + CLI
(`--json`, `--update` to rewrite the lesson-meta in place). Prose excludes
script/style/nav/svg/head/pre; code = non-blank lines in `<pre>`.

**Integration:** `check-lesson.py` gained a warning-only `RT` check (loads the hyphenated
module by path). Warns when declared drifts > max(2, 30%·declared) from the estimate; SKIP if
no declared time; never FAIL (advisory). Verified: RT PASS on calibrated ink 01/02, RT WARN
on `godot 0001-nodes-and-scenes` (declared ~10, est ~4 — a real inflated-time finding).

**Tests:** `tests/test_estimate_read_time.py` (11) — calibration lock + formula (prose WPM,
code penalty, blank-line skip, script/svg skip, 1-min floor) + helpers (parse/update). Full
suite 241 passed; `mise run verify` EXIT 0.
