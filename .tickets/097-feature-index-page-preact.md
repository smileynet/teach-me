---
id: "097"
title: "Convert generate_index_page.py to Preact output"
type: feature
status: open
priority: medium
blocked_by: ["095"]
---

# Convert generate_index_page.py to Preact output

## What to build

Index page (All Lessons dashboard) as Preact components — domain cards with progress rings, topic counts, reactive filtering.

## Deliverables

- Data island with all domains, topic counts, completion stats
- `DomainCard` component showing title, description, progress ring, topic count
- Click-through to domain map page
- Optional: filter/sort by progress

## Acceptance Criteria

- [ ] `python tools/generate_index_page.py --scan-dir X --output Y` produces Preact page
- [ ] Domain cards render with progress indicators
- [ ] Links to map pages work
- [ ] Theme toggle works
- [ ] Loads offline (vendored deps)
