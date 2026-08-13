---
id: "104"
title: "Update scaffolds for Preact mount points"
type: feature
status: done
priority: medium
blocked_by: ["101", "102", "103"]
work_order: 8
---

# Update scaffolds for Preact mount points

## What to build

Update `assets/scaffolds/*.html` templates to reference Preact import map + component mount points instead of vanilla script tags.

## Deliverables

- `assets/scaffolds/lesson.html` — import map, `<div id="lesson-actions">`, module script
- `assets/scaffolds/quiz.html` — import map, `<div id="app">`, module script mounting QuizView
- `assets/scaffolds/quick-check.html` — import map, `<div id="app">`, module script mounting ReviewDeck
- `assets/scaffolds/reference.html` — minimal (static content, action bar mount only)
- Update scaffold README with new conventions

## Acceptance Criteria

- [ ] All scaffolds use import map pointing to vendored deps
- [ ] Mount points clearly marked with comments
- [ ] Data island pattern documented in scaffold comments
- [ ] `mise run verify` passes (link checker finds vendored assets)

## Context & Sources

- **Current scaffolds:** `assets/scaffolds/` — lesson.html, quiz.html, quick-check.html, reference.html
- **New pattern:** Import map + `<div id="app">` or `<div id="lesson-actions">` mount point + `<script type="module">`
- **Helper:** `tools/lib/preact_page.py` — may be used directly or scaffold shows the manual pattern
- **Reference:** `assets/components/` for the component catalog
- **Depends on:** 101, 102, 103 completing first (so we know the final mount-point pattern)
