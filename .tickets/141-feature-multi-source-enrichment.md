---
id: "141"
title: "Feature: multi-source enrichment — compound new sources into existing topics with conflict surfacing"
status: open
blocked_by: ["140"]
---

# Feature: multi-source enrichment

## What to build

When a user provides a second source on a topic that already has lessons, compound the new material into existing content rather than replacing it:

- Existing lesson gains a "Different perspective" section citing the new source
- Conflicts between sources surfaced as pedagogically valuable callouts
- New source-specific questions added alongside existing ones (don't remove old)
- Attribution stays clear: which point came from which source

Inspired by coding-best-practices' "compound don't duplicate" pattern.

## Acceptance criteria

- [ ] Detect when a new source covers an existing topic (topic slug already in MAP.md)
- [ ] Add source-attributed subsection to existing lesson (not replace)
- [ ] Conflicts rendered as distinct UI element ("Sources disagree: A says X, B says Y")
- [ ] New questions added with provenance to new source; existing questions preserved
- [ ] Works for web-researched topics too (second pass adds depth)
