---
id: "097"
title: "Convert generate_index_page.py to Preact output"
type: feature
status: done
priority: medium
blocked_by: ["095"]
work_order: 2
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

## Context & Sources

- **Pattern:** Data island (Python serializes JSON, Preact reads at runtime) — see `.scratch/research/python-to-preact-templating.md`
- **Helper:** `tools/lib/preact_page.py` — `render_page()` generates the HTML shell
- **Components:** `assets/components/` — TopicCard, StatusBadge, store.js patterns to follow
- **Current code:** `tools/generate_index_page.py` (322 lines) — produces vanilla HTML with progress rings
- **Import map:** `assets/import-map.json` — resolved relative paths for vendored deps
