---
id: "044"
title: "Feature: orientation lesson generated from MAP.md"
status: done
priority: medium
blocked_by: ["043"]
type: feature
---

# Feature: orientation lesson from MAP.md

## What to build

When a MAP.md is created, automatically generate an orientation lesson — a 2-3 minute "here's the landscape" page with an inline diagram showing all topics and their relationships.

## Design

The orientation lesson is:
- Title: "[Domain]: The Landscape"
- Content:
  1. What this domain IS (one paragraph, from MAP.md orientation section)
  2. Why it matters (connect to MISSION.md)
  3. Inline SVG diagram showing topics as nodes + prereq edges (via draw-diagram.py --type graph)
  4. Brief description of each subtopic (from the `why` field)
  5. "Pick where to start" prompt (suggest the topic with no prereqs that unlocks the most)

## The diagram

```bash
mise run draw -- --type graph --backend graphviz --data '{
  "nodes": [{"label": "Ingestion", "color": "blue"}, ...],
  "edges": [["ingestion", "storage"], ["storage", "transformation"], ...],
  "groups": []
}'
```

Color vocabulary: blue = available now, gray = has unmet prereqs, green = complete.

## Acceptance criteria

- [ ] Generates a valid lesson HTML from any well-formed MAP.md
- [ ] Diagram shows all topics with prerequisite edges
- [ ] Topic descriptions come from MAP.md `why` fields
- [ ] Lesson ends with "where do you want to start?" + suggestion
- [ ] Follows existing lesson scaffold (CSS variables, theme toggle, accessibility)

## Validation

- **Unit:** `python tools/map_parser.py` parses the source MAP.md without errors
- **Integration:** Generated HTML loads in Playwright with zero console errors
- **E2E:** Start `mise run serve`, navigate to generated orientation lesson, verify diagram renders (SVG present), topic cards visible, theme toggle works, suggestion matches `get_next_suggestion()` output

## Resolution (2026-08-12)

**Superseded by 068.** The map page IS the orientation — a separate lesson page is redundant. The value (guide the user to start) is delivered via a suggestion banner on the map page instead of a separate HTML file.
