# ADR 0002: Research-First Teaching

## Status

Accepted (2026-08-09)

## Context

Lessons written from parametric memory contained factual errors that only surfaced when we researched the domain:

- **Iceberg lesson** (8 issues): wrong layer count, missing delete files, dead library in recommendations, maintenance buried as optional, implied S3 consistency issues fixed since 2020.
- **Roguelike lesson** (premise overturned): taught "ECS is the right architecture" when practitioners say the opposite for first projects; recommended bracket-lib (frozen since 2022) and specs/Legion (both inactive).

Both lessons read well and felt authoritative. Without independent research, neither the agent nor the learner would know they were wrong.

## Decision

Every lesson requires a completed research phase before writing. This is a hard gate in the teach skill.

**Process:**
1. Identify 3-6 subtopics an expert would consider
2. Dispatch research per subtopic (2+ sources, practitioner perspectives, search for warnings)
3. Populate RESOURCES.md with verified sources and trust ratings
4. Write the lesson — every claim traces to a research finding

**Adequacy criteria:**
- 2+ independent sources per major claim
- At least one practitioner source (not just official docs)
- Explicit search for warnings/anti-patterns
- Sources are current (check dates)
- The "look around corners" test: would a domain expert approve this?

## Consequences

- Lessons take longer to produce (research adds 10-15 minutes of subagent time)
- RESOURCES.md is always populated before the first lesson
- Factual accuracy is verifiable — claims link to sources
- The agent cannot teach from memory alone, even for topics it "knows"
- Research artifacts live in `.scratch/research/` (ephemeral); verified sources persist in RESOURCES.md
