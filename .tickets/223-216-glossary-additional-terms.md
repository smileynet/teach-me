---
id: "223"
title: "Additional Terms section for orphaned glossary entries"
status: done
blocked_by: []
priority: high
type: feature
tags: ["ink"]
---

# Fix orphaned glossary entries (terms without inline spans)

## Problem

4 glossary terms across lessons 01 and 04 are defined in the JSON block but never appear in body text with a `<span class="term">` annotation. Tooltips can't trigger because no anchor exists.

Orphaned terms:
- L01: `end-divert` — `-> END` explained extensively, compound label never used
- L04: `tunnel-return` — `->->` explained with gotcha callout, compound label absent
- L04: `inline-calling` — "called inline" in prose but not as hyphenated term
- L04: `pass-by-value` — concept gap: default parameter behavior never explained

## Research Findings (2026-08-26)

### Pedagogical consensus (Mayer coherence principle, Sweller CLT)
- Supplementary terms should be passively available, not actively pushed
- Injecting extra terms into lesson body adds extraneous cognitive load
- Three-tier visibility: Active (tooltip in text) → Discoverable (linked) → Available (glossary page)
- Do NOT add a visible "Additional Terms" section — violates coherence principle

### Revised approach (lighter)
- Ensure each orphaned term has a `<span class="term">` on existing text that already discusses the concept
- `pass-by-value` is a real concept gap → add one sentence to L04
- Other 3 terms just need spans on existing prose

## What to do

1. **Fix `pass-by-value` gap** — one sentence in L04 parameters section: "Parameters are passed by value — the knot receives a copy, not the original variable."
2. **Add spans to existing text:**
   - L01: wrap `-> END` first explanation in `<span class="term" data-term="end-divert">`
   - L04: wrap `->->` in `<span class="term" data-term="tunnel-return">`
   - L04: wrap "called inline" in `<span class="term" data-term="inline-calling">`
   - L04: wrap new pass-by-value sentence in `<span class="term" data-term="pass-by-value">`
3. **check-lesson.py Q15** — warn if glossary key has no matching data-term span in body

## Acceptance criteria

- [x] `pass-by-value` concept explained in L04 (one sentence)
- [x] All 4 orphaned terms have `<span class="term">` in their respective lessons
- [~] check-lesson.py Q15 glossary coverage check added (warning level) — DEFERRED to #228 (verified manually via .scratch coverage script this session; automated check belongs with #228's check-lesson.py additions)
