---
id: "144"
title: "Feature: compounding reference docs — enrich existing pages from new sources"
status: open
blocked_by: ["141"]
priority: low
---

# Feature: compounding reference docs

## Context

Research finding (135-synthesis, coding-best-practices pattern): one canonical page per concept, enriched by every new source. When a second source covers the same concept, add a "Per [Source B]..." subsection rather than a new page.

## What to build

Reference docs grow over time as new sources are added:
- Each concept has ONE reference page (compound-don't-duplicate)
- New sources add attributed subsections under existing headings
- "Sources" table at bottom lists all contributing sources with coverage
- Universal agreements highlighted; divergences noted with attribution
- Meta-synthesis triggered when 3+ sources address the same concept

## Acceptance criteria

- [ ] Reference doc gains new subsection when second source covers same concept
- [ ] Attribution preserved per-claim (not just per-page)
- [ ] "Sources" footer table shows all contributing sources
- [ ] Agreements strengthen (shared by N sources); divergences noted
- [ ] Reference doc never shrinks — only compounds
