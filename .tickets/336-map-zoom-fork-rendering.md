---
id: "336"
title: "Render child-map zoom and cross-map prereqs"
status: open
priority: low
blocked_by: []
type: feature
tags: ["arch-review"]
---

# Render child-map zoom and cross-map prereqs (untracked #155 deferral)

## Why

#155's motivating use case (the godot toon fork: parent domain spawning a child MAP) was deferred "Out of scope Phase 1" with no follow-up ticket — the only plan gap found by the 2026-09-16 architecture review with no ticket home. Half the machinery exists but is dead code.

## As-built (verified 2026-09-16)

- `tools/generate_map_page.py:40-48` imports `find_child_map` / `has_child_maps` / `get_breadcrumb_chain` / `can_zoom_in` and never calls them (grep: import sites only)
- `assets/components/TopicCard.js:53` renders an "Explore subtopics" button with no onClick handler (silent button — violates the visual-teaching steering rule)
- Cross-map prereqs: `map_parser.py:300` drops unresolvable slugs (silently), and the island's `prereqs` = `prereqIds` only (`generate_map_page.py:134,262`), so cross-map prereqs are omitted from the met/unmet list entirely
- Forest-scope prereq resolution DOES exist for validation (`build_forest_index` / `validate_forest`, #260) — rendering just never consumes it

## What to build

- Breadcrumb + zoom: topic map pages navigate to child domain maps when they exist
- Cross-map prereqs surface on TopicCard (met/unmet with a pointer to the owning domain), even when no graph edge renders
- Wire or remove the dead imports; the "Explore subtopics" button either navigates or is deleted

## Acceptance criteria

- [ ] A domain with a child map shows working breadcrumb + zoom navigation (Playwright click-through)
- [ ] A topic whose prereq lives in a sibling/parent map shows that prereq with its owning domain (not silently omitted)
- [ ] No dead graph imports remain in generate_map_page.py; no silent buttons remain in TopicCard.js
- [ ] `python tools/check-maps-forest.py` still passes; `mise run verify` green

## Resolution

TBD
