---
id: "172"
title: "Feature: stale lesson detection from enrichment overlays"
status: open
blocked_by: []
priority: low
---

# Feature: stale lesson detection from enrichment overlays

## What to build

Add `mise run sr:stale` command that reads enrichment overlays and reports topics where a newer source has `outdated` or `factual` conflict signals — indicating the lesson may need regeneration.

## Context

- Enrichment overlays (`sources/{domain}/enrichments.json`) record conflict types per matched topic
- `outdated` and `factual` conflicts indicate the existing lesson content may be wrong or superseded
- No mechanism currently alerts the user that a lesson needs updating after new source ingestion
- ~60 lines as a new script or addition to sr-status.py

## Acceptance criteria

- [ ] `mise run sr:stale` reads all enrichment overlay files in the workspace
- [ ] Reports topics with `outdated` or `factual` conflict_type
- [ ] Shows: topic slug, conflict type, signal details, which source triggered it
- [ ] Exit code 0 if no stale topics, 1 if stale topics found
- [ ] Works when no enrichment overlays exist (reports "no enrichments found")

## Validation

- [ ] Workspace with an outdated conflict → reported
- [ ] Workspace with only complementary matches → clean
- [ ] Workspace with no enrichments → graceful "no enrichments found"
