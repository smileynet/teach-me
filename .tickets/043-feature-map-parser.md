---
id: "043"
title: "Feature: MAP.md parser and data model"
status: open
priority: high
blocked_by: []
type: feature
---

# Feature: MAP.md parser and data model

## What to build

A parser that reads MAP.md files and exposes the domain graph as a queryable data structure for the teach skill.

## Design

Parse MAP.md frontmatter (domain, parent, depth, leads_to) + topic blocks (title, why, prereqs, status). Validate constraints.

### Data model

```python
@dataclass
class Topic:
    slug: str
    title: str
    why: str
    prereqs: list[str]
    status: str  # not-started | in-progress | complete

@dataclass
class DomainMap:
    domain: str
    description: str
    parent: str | None
    depth: int
    leads_to: list[str]
    orientation: str
    topics: list[Topic]
```

### Operations

- `load_map(path) -> DomainMap`
- `update_status(path, topic_slug, new_status)`
- `get_available_topics(map) -> list[Topic]` (prereqs satisfied)
- `get_next_suggestion(map) -> Topic` (available + most dependents)
- `validate(map) -> list[str]` (errors: cycles, undefined prereqs, >9 topics)

## Acceptance criteria

- [ ] Parses the MAP.md format from the proposal correctly
- [ ] Rejects maps with cycles, undefined prereqs, or >9 topics
- [ ] Updates status field without clobbering other content
- [ ] `get_available_topics` respects prereq completion
- [ ] Handles missing MAP.md gracefully (not a crash)
