# MAP.md Format Specification

A MAP.md describes a learning domain — 5-9 subtopics the learner can explore, with soft prerequisites showing relationships and leads_to showing where the knowledge goes next.

## Structure

```markdown
---
domain: slug-for-this-domain
description: "One sentence: what the learner will understand after exploring this map"
generated: YYYY-MM-DD
depth: 0          # 0 = root domain, 1 = zoomed subtopic, 2 = sub-subtopic
parent: null      # slug of parent MAP.md (null for root)
leads_to:         # supertopics: what domains this knowledge unlocks
  - domain-slug-1
  - domain-slug-2
---

# Human-Readable Domain Title

## Orientation

2-3 sentences framing what this domain covers and why it matters.
This text is used verbatim in the orientation lesson.

## Topics

### topic-slug
- **title:** Human-Readable Topic Name
- **why:** One sentence connecting this topic to the domain goal
- **scope:** lightweight | substantial | deep (expected effort)
- **prereqs:** [other-topic-slug, another-slug]  # soft — suggestions, not gates
- **leads_to:** [topic-in-another-domain]  # optional — where this specific topic leads
- **status:** not-started | in-progress | complete
```

## Rules

1. **5-9 topics per MAP.md** — hard constraint. Fewer = not a domain (just teach it). More = needs splitting.
2. **No cycles in prereqs** — the graph must be a DAG within one map.
3. **All prereq references must resolve** — every slug in prereqs[] must match an ### heading in the same file.
4. **Soft prerequisites** — framed as "You'll get more from this if you know X". Never gates.
5. **Scope markers** — lightweight (~1 lesson), substantial (2-3 lessons), deep (4+ lessons, may warrant its own sub-MAP).
6. **leads_to is forward-looking** — domains that become accessible after completing THIS domain. Don't need to exist yet.
7. **Status is learner state** — updated by the teach skill after lessons/quiz-me, not by the map generator.
8. **Orientation is concise** — 2-3 sentences max. Detail lives in the orientation lesson, not here.

## Example

```markdown
---
domain: modern-data-analytics-stacks
description: "Understand how data moves from sources through transformation to analyst-facing tools"
generated: 2026-08-11
depth: 0
parent: null
leads_to:
  - data-governance-at-scale
  - streaming-architectures
  - platform-engineering
---

# Modern Data Analytics Stacks

## Orientation

You'll understand how analytics data flows from operational systems through storage and transformation layers to dashboards. By the end, you can evaluate stack choices and explain tradeoffs to a team.

## Topics

### ingestion
- **title:** Data Ingestion
- **why:** Data has to get into the system before anything else happens
- **scope:** substantial
- **prereqs:** []
- **status:** not-started

### storage
- **title:** Storage & Table Formats
- **why:** Where data lives determines what queries are possible and how fast
- **scope:** deep
- **prereqs:** [ingestion]
- **status:** not-started
```

## Recursive Zoom

When a learner "zooms in" on a topic, a new MAP.md is generated for that subtopic:
- File: `{topic-slug}.MAP.md` (flat namespace)
- Frontmatter: `parent: {parent-domain-slug}`, `depth: {parent-depth + 1}`
- Max depth: 3 (at depth 3, suggest real resources instead of more maps)

## Supertopics

`leads_to` at the domain level names what becomes accessible after the full map is explored.
Individual topics can also have `leads_to` pointing to specific external topics — this is optional and used sparingly.

Supertopics are presented:
- At domain completion ("this knowledge opens up: [list]")
- On request ("where does this lead?")
- Never as obligation — always opportunity framing
