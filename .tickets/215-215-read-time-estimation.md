---
id: "215"
title: "Read-time estimation tooling"
status: open
blocked_by: []
priority: high
type: feature
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

- [ ] Research complete: formula validated against lessons 01 + 02 as calibration
- [ ] `tools/estimate-read-time.py` exists, stdlib-only
- [ ] Running on lesson 01 produces ~8 min; on lesson 02 produces ~12 min (±2 min)
- [ ] Integrated with `check-lesson.py` as a warning (not blocking)
- [ ] Formula documented in a comment or README
