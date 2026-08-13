# MAP.md Format Specification

A MAP.md describes a learning domain — 5-9 subtopics the learner can explore, with soft prerequisites showing natural relationships and leads_to showing where the knowledge goes next.

## Structure

```markdown
---
domain: slug-for-this-domain
description: "One sentence: what the learner will understand after exploring this map"
generated: YYYY-MM-DD
depth: 0          # 0 = root domain, 1 = zoomed subtopic, 2 = sub-subtopic
parent: null      # slug of parent MAP.md (null for root)
leads_to:         # what domains this knowledge unlocks (with descriptions)
  - slug: domain-slug-1
    why: "One sentence explaining what this opens up"
  - slug: domain-slug-2
    why: "One sentence explaining what this opens up"
---

# Human-Readable Domain Title

## Orientation

2-3 sentences framing what this domain covers and why it matters.
This text is used verbatim in the orientation lesson.

## Topics

### topic-slug
- **title:** Human-Readable Topic Name
- **why:** One sentence connecting this topic to the domain goal
- **prereqs:** [other-topic-slug, another-slug]  # soft — suggestions, not gates
- **status:** not-started | in-progress | complete
```

## Rules

1. **5-9 topics per MAP.md** — hard constraint. Fewer = not a domain (just teach it). More = needs splitting.
2. **No cycles in prereqs** — the graph must be a DAG within one map.
3. **All prereq references must resolve** — every slug in prereqs[] must match an ### heading in the same file.
4. **Soft prerequisites** — framed as "You'll get more from this if you know X". Never gates.
5. **Natural branching** — prereqs express genuine dependencies, not a forced linear order. If two topics can be learned in parallel, don't chain them. Let the DAG branch and converge naturally.
6. **No scope markers** — topics don't carry effort estimates. The learner doesn't need to know how "big" a topic is before starting it.
7. **leads_to needs descriptions** — every leads_to item has a `slug` and a `why` (one sentence explaining what it opens up). Bare slugs render as unlabeled buttons — useless to the learner.
8. **Status is learner state** — updated by the teach skill after lessons/quiz-me, not by the map generator.
9. **Orientation is concise** — 2-3 sentences max. Detail lives in the orientation lesson, not here.

## Example

```markdown
---
domain: modern-data-analytics-stacks
description: "Understand how data moves from sources through transformation to analyst-facing tools"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - slug: streaming-architectures
    why: "Process data in real-time instead of batch"
  - slug: platform-engineering
    why: "Build internal developer platforms on top of your data stack"
---

# Modern Data Analytics Stacks

## Orientation

You'll understand how analytics data flows from operational systems through storage and transformation layers to dashboards. By the end, you can evaluate stack choices and explain tradeoffs to a team.

## Topics

### ingestion
- **title:** Data Ingestion
- **why:** Data has to get into the system before anything else happens
- **prereqs:** []
- **status:** not-started

### storage
- **title:** Storage & Table Formats
- **why:** Where data lives determines what queries are possible and how fast
- **prereqs:** [ingestion]
- **status:** not-started
```

## Subtopic Maps

When a learner wants to go deeper on a topic, a new MAP.md is generated:
- File: `{topic-slug}.MAP.md` (flat namespace in `maps/`)
- Frontmatter: `parent: {parent-domain-slug}`, `depth: {parent-depth + 1}`
- Max depth: 3 (at depth 3, suggest real resources instead of more maps)
- The button is labeled "Explore subtopics" — breaks the topic into 3-5 focused sub-topics

## Leads-To (Supertopics)

`leads_to` at the domain level names what becomes accessible after the full map is explored. Each item is a button with a one-sentence description.

Rendered as:
- Styled buttons with the domain name and why-sentence
- At domain completion or on request
- Never as obligation — always opportunity framing
