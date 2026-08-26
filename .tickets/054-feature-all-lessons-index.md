---
id: "054"
title: "Feature: All Lessons index page — card grid of all domains"
status: done
priority: high
blocked_by: []
type: feature
tags: [platform]
---

# Feature: All Lessons index page

## What to build

A top-level `lessons/index.html` page showing all learning domains as a card grid. This is the "← All Lessons" target from the breadcrumb nav. Serves as the learner's personal dashboard.

## Design

### Layout

Card grid using `repeat(auto-fill, minmax(280px, 1fr))` — responsive, scannable, no forced connections between unrelated domains.

Each card shows:
- Domain title
- Orientation text (first sentence)
- Progress ring (SVG: complete/total topics)
- Status: "3 of 7 topics explored"
- Click → navigates to that domain's map page

### Generation

`tools/generate_index_page.py`:
1. Scan for `*.MAP.md` and `MAP.md` at project root (depth 0 maps only)
2. Parse frontmatter + count topic statuses
3. Output `lessons/index.html`

### Navigation hierarchy

```
lessons/index.html        ← "All Lessons" (the dashboard)
  └── lessons/map.html    ← "Domain Map" (one per domain)
       └── lessons/*.html ← Individual lessons
```

### What it does NOT do

- No forced connections between domains
- No ranking/prioritization (alphabetical or last-activity sort)
- No recommendation engine ("you should try X next")
- No backend — static HTML regenerated on demand

## CLI

```bash
mise run index:generate   # scan all MAP.md files, produce index.html
```

## Acceptance criteria

- [x] Generates `lessons/index.html` from all depth-0 MAP.md files
- [x] Each domain shows as a card with title, description, progress
- [x] Progress ring (SVG) shows complete/total ratio
- [x] Card click navigates to that domain's map.html
- [x] Works with 1 domain and with 5+ domains
- [x] Breadcrumb on map page ("← All Lessons") links here
