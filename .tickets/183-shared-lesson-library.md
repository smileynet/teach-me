---
id: "183"
title: "Shared lesson library with local-only user state"
status: open
blocked_by: ["213", "214", "221"]
priority: high
tags: [platform]
---

# Shared lesson library with local-only user state

## Context

Lessons are currently generated per-workspace and gitignored. The new model: lessons are a **shared, committed resource** that users generate and contribute back to the repo. Personal state (completion, progress, preferences) stays local-only.

This inverts the current architecture — lessons move from ephemeral/local to shared/versioned, while user state moves from "tracked alongside content" to strictly local.

**Decided by ADR 0012 (accepted 2026-08-28):** this ticket implements the
public-library half of the two-tier content model. It **supersedes #071's**
"all user content lives in gitignored `workspace/`" decision and the serve
default from #245/ADR 0011. The committed library lives under **`library/`**
(today's `examples/`, renamed) — see the rename scope below. #184 implements the
private `.user/` overlay on top of this.

## What to build

1. **Lessons as committed content** — generated lessons live in the repo (e.g., `lessons/{domain}/`) and are committed + pushed. Any user can generate a lesson and contribute it.

2. **Local user config** — a gitignored file (e.g., `.user/state.json` or similar) tracks per-user state:
   - Completion status per topic
   - SR card progress/scores
   - Reading preferences (already handled by localStorage, but any file-based state belongs here)

3. **Separation of concerns** — the repo contains: lessons, maps, quizzes, reference docs, SR card definitions. The user config contains: which ones I've completed, my review schedule, my scores.

4. **Contribution flow** — when a user generates a new lesson, it lands in the committed tree ready to PR/push. Other users pulling the repo get the lesson immediately.

5. **Rename `examples/` → `library/`** (ADR 0012). This is the mechanical part
   that makes the committed tree *the* library:
   - `git mv examples library`
   - Update serve.py (default workspace resolution + any `examples/` fallback
     paths), `tools/map_parser` path assumptions, and mise tasks that reference
     `examples/` (`serve`, `maps:regenerate`, `index:generate`, `verify`).
   - Update README example-workspace links and the AGENTS.md workspace-layout
     section + `examples/` mentions.
   - Confirm `.gitignore` still ignores only the private path — after the
     2026-08-28 anchoring (`/workspace/`), `library/` is tracked with no
     `git add -f` needed.

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
- [ ] `examples/` renamed to `library/`; serve.py, map_parser, mise tasks, README, and AGENTS.md updated to match
- [ ] Fresh clone `mise run serve` serves the `library/` content (not an empty auto-created `workspace/`) — supersedes ADR 0011's first-launch default
- [ ] `library/` is tracked without `git add -f`; only `.user/` and per-user state remain gitignored
