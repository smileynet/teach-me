---
id: "110"
title: "Themed resources page with source trust ratings"
type: feature
status: done
priority: high
blocked_by: []
---

# Themed resources page with source trust ratings

## What to build

A Preact page that renders RESOURCES.md as a themed, filterable table of verified sources with trust ratings. Accessible from the index page and from lesson action bars ("View sources").

## Current state

- RESOURCES.md is served as raw markdown (unthemed, no navigation)
- Learners have no way to discover or verify sources from within the lesson flow
- Trust ratings (★/★★/★★★) exist in RESOURCES.md but aren't actionable

## Desired state

- Dedicated `/resources.html` page with themed cards/table for each source
- Filterable by domain/topic (when workspace has multiple domains)
- Trust ratings displayed visually (not just text stars)
- Linked from: index page footer, lesson action bars, reference docs
- Lesson citations link to this page (anchored to the specific source)

## Acceptance Criteria

- [x] `python tools/generate_resources_page.py --workspace X --output Y` produces Preact page
- [x] Parses RESOURCES.md markdown table format into structured data
- [x] Sources rendered as cards with: title, URL, trust rating, what it covers
- [x] Dark/light theme works
- [x] Linked from index page
- [x] Linked from lesson action bar (LessonActions component)

## Context

- RESOURCES.md format: markdown tables with Source | Trust | Notes columns
- Pattern: data island + Preact page (same as quiz/review pages)
- Helper: `tools/lib/preact_page.py`
- Workspace file: `workspace/RESOURCES.md`

## Resolution (2026-08-13)

TBD
