---
id: "136"
title: "Apply provenance chain, conflict synthesis, and cognitive load separation across teach-me"
status: done
blocked_by: ["135"]
priority: high
tags: [source-ingest, platform]
---

# Apply provenance patterns across teach-me

## What to build

Use subagents to analyze the research findings from #135 and the reference project studies (rustacean-academy, coding-best-practices) and propose how to apply the discovered patterns beyond just "teach from docs" — across the entire teach-me platform:

1. **Provenance chain for web-researched content** — Should existing lessons gain source-quote traceability? How would we retrofit this without regenerating everything?

2. **Conflict surfacing in existing lessons** — When web research finds disagreeing sources, should lessons surface this? How would it appear in the UI?

3. **Cognitive load separation in existing pipeline** — Should we split "core concept" from "best practices / edge cases" in lesson generation? What changes in the generate-topic skill?

4. **Situation index / symptom-first navigation** — Could map pages gain an alternative entry point: "I'm stuck on X" → relevant topic? How would this work with the DAG layout?

5. **Author-as-perspective teaching** — For topics with multiple schools of thought, should teach-me offer "view from perspective of [X]"? Where does this add value vs complexity?

## Acceptance criteria

- [x] Subagent analysis of each pattern (4 stages: provenance, cognitive load, conflicts+situation, answer gate)
- [x] Proposal with scope + effort in ADR 0007
- [x] Decision recorded in .memory/adr/0007-adopt-research-patterns.md
- [x] Conventions adopted in generate-topic SKILL.md (no separate tickets needed — guidance-only changes)
