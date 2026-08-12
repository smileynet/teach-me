---
id: "045"
title: "Feature: zoom in/out — recursive subtopic navigation"
status: open
priority: medium
blocked_by: ["043"]
type: feature
---

# Feature: zoom in/out navigation

## What to build

When a learner says "go deeper on storage", the teach skill generates (or loads) a sub-MAP.md for that topic and navigates into it. "Zoom out" returns to the parent.

## Design

### Zoom in

1. Learner: "zoom in on storage" / "go deeper on storage" / "I want to learn more about storage layers"
2. Agent checks: does `storage.MAP.md` exist?
   - **Yes:** Load it, present its orientation, ask where to start
   - **No:** Research that subtopic space, generate `storage.MAP.md`, present orientation
3. The sub-MAP.md has `parent: modern-data-analytics-stacks` and `depth: 1`

### Zoom out

1. Learner: "zoom out" / "big picture" / "go back"
2. Agent reads the current MAP.md's `parent` field
3. Loads and presents the parent MAP.md

### File naming (flat, v1)

```
MAP.md                      # root domain (depth 0)
storage.MAP.md              # depth 1 zoom
storage--object-storage.MAP.md  # depth 2 zoom
```

`parent:` field in frontmatter links back up. `--` separator makes depth visible.

### Depth limit

Max 3 levels deep. At depth 3, suggest real resources (books, courses, docs) instead of more maps. A map of 2-3 subtopics with 2-3 sub-subtopics each is sufficient for casual exploration.

### Trigger phrases

| Phrase | Action |
|--------|--------|
| "zoom in on [X]" / "go deeper on [X]" | Generate or load subtopic MAP.md |
| "zoom out" / "big picture" / "go back" | Navigate to parent MAP.md |
| "show me the map" | Re-present current MAP.md |

## Acceptance criteria

- [ ] "zoom in on X" generates X.MAP.md if it doesn't exist
- [ ] Generated sub-MAP has correct parent + depth fields
- [ ] "zoom out" returns to parent
- [ ] Works 2 levels deep (zoom in on storage → zoom in on object-storage → zoom out → zoom out)
- [ ] Depth limit (3) produces a suggestion instead of another map

## Validation

- **Unit:** `load_map` on generated sub-MAP parses correctly; `validate` passes; parent/depth fields correct
- **Integration:** Parent map's `leads_to` or topic `lesson_file` links resolve to the child map page
- **E2E (Playwright):** Navigate to parent map → click a "zoom in" node → verify child map page loads with back-link → click "zoom out" → verify returns to parent. Repeat at depth 2.
