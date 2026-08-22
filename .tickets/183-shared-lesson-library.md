---
id: "183"
title: "Shared lesson library with local-only user state"
status: open
blocked_by: []
priority: high
---

# Shared lesson library with local-only user state

## Context

Lessons are currently generated per-workspace and gitignored. The new model: lessons are a **shared, committed resource** that users generate and contribute back to the repo. Personal state (completion, progress, preferences) stays local-only.

This inverts the current architecture — lessons move from ephemeral/local to shared/versioned, while user state moves from "tracked alongside content" to strictly local.

## What to build

1. **Lessons as committed content** — generated lessons live in the repo (e.g., `lessons/{domain}/`) and are committed + pushed. Any user can generate a lesson and contribute it.

2. **Local user config** — a gitignored file (e.g., `.user/state.json` or similar) tracks per-user state:
   - Completion status per topic
   - SR card progress/scores
   - Reading preferences (already handled by localStorage, but any file-based state belongs here)

3. **Separation of concerns** — the repo contains: lessons, maps, quizzes, reference docs, SR card definitions. The user config contains: which ones I've completed, my review schedule, my scores.

4. **Contribution flow** — when a user generates a new lesson, it lands in the committed tree ready to PR/push. Other users pulling the repo get the lesson immediately.

## Design questions

- Where does SR card *definition* live (shared) vs SR card *review state* (local)?
- How does the index/map page read completion status from local config?
- Does the local config need migration/versioning as the schema evolves?
- What happens when a shared lesson is updated — does local completion reset?

## Acceptance criteria

- [ ] Lessons are committed to the repo (not gitignored)
- [ ] Completion/progress state is local-only (gitignored)
- [ ] Index and map pages read local state to show completion badges
- [ ] A new user cloning the repo sees all lessons but zero completion
- [ ] Generating a lesson produces a committable file (not in a gitignored directory)
- [ ] SR card definitions are shared; review progress is local
- [ ] Existing workspace content migrated or migration path documented
