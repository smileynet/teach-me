---
id: "347"
title: "Deep-dive lesson quality across every shipped domain"
status: in_progress
priority: low
blocked_by: []
type: research
tags: ["arch-review", "content"]
validation_criteria:
  - "Audit samples every shipped domain and page type"
  - "Claims, citations, artifacts, accessibility, and teaching patterns use a recorded rubric"
  - "Confirmed corpus-wide gaps have scoped follow-up tickets"
---

# Deep-dive lesson quality across every shipped domain

## Intent source

Follow-up proposed by the architecture review. Structural verification is strong, but
pedagogical and evidentiary quality was only spot-checked.

## What to review

Evaluate every domain against `.kiro/steering/visual-teaching.md`: knowledgeable-colleague
tone, mechanics framing, sources, code narrative, runnable artifacts, honest visuals,
accessible interactions, quiz quality, glossary coverage, and silent controls.

## Context

Read the steering file, page scaffolds, `tools/check-lesson.py`,
`tools/check-lesson-code.py`, and one full topic chain per domain before fixing the rubric.

## Acceptance criteria

- [ ] The rubric separates mechanical checks from judgment-based teaching quality
- [ ] Every domain and page type appears in the sample matrix
- [ ] Citations are checked for support, not only reachability
- [ ] Runnable artifacts use their real toolchains where available
- [ ] Corpus-wide patterns and isolated defects are reported separately
- [ ] Confirmed gaps receive scoped tickets

## Resolution

TBD
