---
id: "120"
title: "Feature: Lesson versioning — preserve and revert across rewrites"
status: open
blocked_by: []
---

# Feature: Lesson versioning — preserve and revert across rewrites

## What to build

When a lesson is rewritten/regenerated, preserve the previous version so the user can compare or revert. Lessons evolve — sometimes a rewrite is worse than the original, or the user wants to compare how the explanation changed. This needs a lightweight versioning mechanism (not full git history, but accessible from the UI).

## Acceptance criteria

- [ ] Before overwriting a lesson, the previous version is saved (e.g., `0002-topic.v1.html`)
- [ ] User can view previous versions from the lesson page or action bar
- [ ] User can revert to a previous version (restores it as the current lesson)
- [ ] Version history is visible (list of dates/versions with brief diff summary)
- [ ] Reference docs and quiz content are also versioned alongside the lesson
- [ ] Works on GitHub Pages (static file approach) — no database required
- [ ] Old versions don't clutter the main lessons directory (subfolder or naming convention)
