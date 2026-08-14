---
id: "118"
title: "Feature: Rewriting a lesson auto-resets its complete status"
status: done
blocked_by: []
---

# Feature: Rewriting a lesson auto-resets its complete status

## What to build

When the user asks to regenerate/rewrite a lesson that was previously marked complete, the system should automatically reset the topic's status from "complete" back to "in-progress" in MAP.md (and regenerate the map page). The user shouldn't have to manually un-check completion after a rewrite.

## Acceptance criteria

- [ ] When generate-topic runs on an already-complete topic, status resets to in-progress
- [ ] MAP.md is updated and map page is regenerated
- [ ] The quiz and SR questions for that topic are also regenerated (not stale from old content)
- [ ] User is informed of the status reset ("Rewrote lesson — reset status to in-progress")
- [ ] Does NOT reset status if running verification-only (idempotent check, no content change)

## Resolution (2026-08-14)

Phase 2 of generate-topic now resets complete→in-progress on rewrite. Old quiz/SR deleted. User marks complete after review.
