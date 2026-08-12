# ADR 0004: MAP.md Domain Scaffolding

## Status

Accepted (2026-08-11)

## Context

When a learner asks about a broad domain ("teach me about modern data analytics stacks"), a single lesson can't cover it meaningfully. The system needs a way to decompose domains into explorable subtopics with soft prerequisites and forward-looking connections.

Options considered:
- **A. Topic tree** (nested directories per subtopic) — too rigid, implies hierarchy
- **B. Guided curriculum** (flat adaptive sequence) — no persistent map, no discovery
- **C. Knowledge map** (explicit graph with prereqs) — best for casual exploration

## Decision

Use **MAP.md** as a static markdown artifact that describes a learning domain:
- YAML frontmatter: domain slug, parent, depth, leads_to (supertopics)
- 5-9 topic blocks with title, why, scope, prereqs, status
- Generates an interactive HTML page with Graphviz DAG + clickable nodes
- Recursive: any subtopic can become its own MAP.md via "zoom in"
- Supertopics via `leads_to` show where knowledge leads after completion

Key constraints:
- 5-9 topics per map (cognitive load ceiling)
- Soft prerequisites ("easier if you know X") — never gates
- Static artifact, not regenerated per session
- Any entry point valid — learner picks, system doesn't prescribe order

## Consequences

- New format spec at `.memory/map-format-spec.md`
- New tools: `generate_map_page.py`, `generate_index_page.py`
- Teach skill needs big-request detection (ticket 042) and MAP.md generation logic
- Navigation hierarchy: All Lessons → Domain Map → Topic → Lesson
- Supersedes ticket 036 (export knowledge objects) — MAP.md + lessons IS the portable artifact
