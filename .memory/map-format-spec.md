# MAP.md Format Specification

A MAP.md describes a learning domain — up to 9 subtopics (5 is the authoring floor) the learner can explore, with soft prerequisites showing natural relationships and leads_to showing where the knowledge goes next.

The committed MAP.md is **shared content only**. Learner status is never authored here —
it lives in the gitignored `{workspace}/.user/status-overlay.json`, keyed by topic ULID
(`tools/lib/overlay.py`, ADR-0014). Readiness/progress is derived at runtime by joining
the committed graph with the overlay.

This spec documents the parser as built (`tools/map_parser.py`).

## Structure

```markdown
---
domain: slug-for-this-domain
description: "One sentence: what the learner will understand after exploring this map"
depth: 0          # 0 = root domain, 1 = zoomed subtopic, 2 = sub-subtopic (max 3)
parent: null      # slug of parent MAP.md (null for root)
leads_to:         # what domains this knowledge unlocks (with descriptions)
  - slug: domain-slug-1
    why: "One sentence explaining what this opens up"
---

# Human-Readable Domain Title

## Orientation

2-3 sentences framing what this domain covers and why it matters.
This text is used verbatim in the orientation lesson.

## Topics

### topic-slug
- **id:** 01M174TQPPZFGSZT3DJNFGXHZ9   # ULID — minted if absent, then never edited
- **title:** Human-Readable Topic Name
- **why:** One sentence connecting this topic to the domain goal
- **prereqs:** [other-topic-slug, another-slug]  # soft — suggestions, not gates
- **soft_prereqs:** [adjacent-slug]              # associative links → related edges
- **scope:** lightweight | substantial | deep    # default substantial
- **lesson_file:** 03-specific-lesson.html       # explicit lesson link (optional)
- **aliases:** [old-slug]                        # former slugs; resolve renames (optional)

## Edges                                                          # optional section

- from: topic-slug
  to: other-topic-slug
  type: prereq          # one of: prereq | leads_to | related
  why: One sentence — why this relationship exists
```

## Topic fields

| Field | Meaning |
|-------|---------|
| `id` | Immutable ULID identity. Minted on parse if absent (`tools/migrate_map_ids.py` persists it); validated for format + uniqueness. Never hand-edit or reuse. Edges and the status overlay key on it; `slug` is display/routing only. |
| `title` | Human-readable name. |
| `why` | One sentence connecting the topic to the domain goal. |
| `prereqs` | Slug list. Soft/informational — never gates. Synthesizes `prereq` edges. |
| `soft_prereqs` | Slug list of associative links. Parsed like prereqs; becomes symmetric `related` edges (NOT weak prereqs). |
| `scope` | `lightweight \| substantial \| deep` (default `substantial`). Effort signal surfaced in the API/UI. |
| `lesson_file` | Explicit lesson filename when it doesn't match the slug convention. |
| `aliases` | Former slugs, used to resolve references after a rename without touching edges. |

**No `status` field.** Learner status is per-user overlay state and is never committed.

## Edges

Closed vocabulary: `prereq` | `leads_to` | `related` (`EDGE_TYPES` in `map_parser.py`).

- Authored **by slug** in a `## Edges` block (`from`/`to`/`type`/`why`); resolved to
  ULID endpoints at parse time. MAP.md never contains a ULID inside an edge.
- `prereq` edges are also synthesized from each topic's `prereqs` list.
- `related` is symmetric — stored once, surfaced both directions (also derived from
  `soft_prereqs`).
- `why` annotations are what make relationships discoverable; prefer them.
- Cycle detection runs on `prereq` edges only — `leads_to`/`related` may be cyclic.

## Frontmatter

- `domain` must match the filename's domain; the map page output derives from it.
- `leads_to` (domain level) accepts three authoring forms: the block list of
  `{slug, why}` shown above, an inline flow list `[slug-a, slug-b]`, or bare strings
  (`why` defaults to empty). Block form is preferred — Rule 7.
- `generated:` survives in files as authoring metadata but is **not parsed** by
  `load_map`.

## Rules

1. **At most 9 topics per MAP.md** — enforced by `validate()`. Fewer than 5 is an
   authoring guideline (not validated); more than 9 needs splitting.
2. **No cycles in prereqs** — the prereq subgraph must be a DAG within one map.
3. **Prereq references must resolve** — per-map `validate()` requires in-file
   resolution; the shipped forest gate (`tools/check-maps-forest.py` →
   `validate_forest`, #155/#260) additionally allows prereqs resolving in any sibling
   map of the forest (cross-map prereqs are legal, resolved via slug/alias union).
4. **Soft prerequisites** — framed as "You'll get more from this if you know X". Never gates.
5. **Natural branching** — prereqs express genuine dependencies, not a forced linear order. If two topics can be learned in parallel, don't chain them.
6. **Topics carry a `scope` effort marker** (`lightweight|substantial|deep`, default
   `substantial`) — surfaced through `/api/map` and the UI. (Supersedes the old
   "no scope markers" rule; the parser and shipped maps carry `scope`.)
7. **leads_to needs descriptions** — every leads_to item should have a `slug` and a `why` (one sentence explaining what it opens up). Bare slugs render as unlabeled buttons — useless to the learner.
8. **Learner status is never committed** — no `status` field in MAP.md. Status lives in
   the gitignored `.user/` overlay keyed by ULID node id; `migrate_strip_status.py`
   removes any straggler lines (#258).
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
- **id:** 01M174TQPPZFGSZT3DJNFGXHZ9
- **title:** Data Ingestion
- **why:** Data has to get into the system before anything else happens
- **prereqs:** []

### storage
- **id:** 01M174TR2N1E4W9QZK5HK0AXTV
- **title:** Storage & Table Formats
- **why:** Where data lives determines what queries are possible and how fast
- **prereqs:** [ingestion]
```

## Subtopic Maps

When a learner wants to go deeper on a topic, a new MAP.md is generated:
- File: `{topic-slug}.MAP.md` (flat namespace in `maps/`); `find_child_map` also
  matches the `*--{topic-slug}.MAP.md` form used by deeper children
- Frontmatter: `parent: {parent-domain-slug}`, `depth: {parent-depth + 1}`
- Max depth: 3 (at depth 3, suggest real resources instead of more maps)
- The button is labeled "Explore subtopics" — breaks the topic into 3-5 focused sub-topics

## Leads-To (Supertopics)

`leads_to` at the domain level names what becomes accessible after the full map is explored. Each item is a button with a one-sentence description.

Rendered as:
- Styled buttons with the domain name and why-sentence
- At domain completion or on request
- Never as obligation — always opportunity framing

Topic-level `leads_to` typed edges (via `## Edges`) stay within one map file; the
cross-domain discovery surface is the domain-frontmatter `leads_to` list rendered by
the forest/index views.
