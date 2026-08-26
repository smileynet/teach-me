---
id: "167"
title: "Detect and track subtopics that introduce new concept areas"
status: open
blocked_by: ["165"]
tags: [content-quality]
---

# Detect and track subtopics that introduce new concept areas

## Context

Lessons naturally introduce concepts from adjacent domains (e.g., toon-banding introduces GradientTexture1D and shader globals — both full topics in their own right). Currently these get mentioned inline without:
1. Sufficient background for unfamiliar readers
2. Links to dive deeper
3. Any tracking for future topic generation

Discovered during toon-banding review: the curve texture approach mentions GradientTexture1D and shader globals as if they're already known. A reader coming from the previous lesson has no basis for either concept.

## What to build

### Layer 1: Inline treatment (convention, enforced by skills)

When a lesson introduces a concept that's NOT already a topic in the domain MAP:
- Add it to `glossary-data` with a clear definition
- Add a `.note` callout with 2-3 sentences of background + a "Read more" link to official docs
- Phrase as "New concept — [term]:" to signal it's not expected prior knowledge

### Layer 2: MAP.md expansion section

Add `## Expansion Opportunities` to domain MAP.md files:
```markdown
## Expansion Opportunities

Subtopics surfaced during lesson development:

- **slug** — brief description (surfaced in: topic-that-introduced-it)
```

These are seeds, not committed topics. No prereqs, no scope. Promoted to real topics when the learner asks or the map needs growth.

### Layer 3: Detection during generation (generate-topic skill)

Add a post-process step (Phase 3) to the generate-topic pipeline:

1. Scan the generated lesson body for:
   - Glossary terms that don't match any existing topic slug in the MAP
   - `.note` blocks containing "New concept" framing
   - External documentation links (docs.godotengine.org, etc.) for concepts not in the topic list
2. For each detected subtopic:
   - Verify it's not already in the MAP (topic or expansion list)
   - Append to `## Expansion Opportunities` in the domain's MAP.md
   - Report to user: "Surfaced potential topics: [X], [Y] — added to expansion list"

### Layer 4: Promotion path

When user asks "teach me more about [expansion topic]":
- Promote from Expansion Opportunities to a real topic entry (with prereqs = the lesson that surfaced it)
- Remove from expansion list
- Generate normally via the existing pipeline

## Acceptance criteria

- [ ] generate-topic skill documents the inline treatment convention (glossary + note + link)
- [ ] generate-topic Phase 3 includes subtopic detection step
- [ ] MAP.md format supports `## Expansion Opportunities` section
- [ ] Detected subtopics are appended to MAP.md automatically during generation
- [ ] Agent reports surfaced subtopics to the user after generation
- [ ] Teach skill knows how to promote expansion items to full topics
