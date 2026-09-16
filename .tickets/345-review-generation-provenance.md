---
id: "345"
title: "Deep-dive generated-artifact reproducibility and provenance"
status: in_progress
priority: medium
blocked_by: ["331", "342"]
type: research
tags: ["arch-review", "research"]
validation_criteria:
  - "Every generated artifact class has a documented source and regeneration command"
  - "A two-run regeneration matrix reports identical output or explained differences"
  - "Claim citations and build provenance are evaluated separately"
---

# Deep-dive generated-artifact reproducibility and provenance

## Intent source

Follow-up proposed by the architecture review's prior-art comparison. Committed generated
pages require deterministic regeneration and traceable inputs.

## What to review

Inventory lessons, references, quizzes, maps, indexes, diagrams, exports, and static-site
output. Identify canonical inputs, generator versions, timestamps/random IDs, ordering,
source citations, and drift gates. Separate evidence provenance from build provenance.

## Context

Read `.memory/specs/environment-gotchas.md`, `tools/check-index-drift.py`,
`tools/assemble-site.sh`, `tools/site-dry-run.py`, source-ingest tools, and
#278/#279/#280/#316. Use authoritative reproducible-build/provenance sources.

## Acceptance criteria

- [ ] Inventory names source, generator, output, and drift gate for every artifact class
- [ ] Two clean regeneration runs cover all domains and report exact diffs
- [ ] Machine paths, locale, current time, random identity, and file ordering are tested
- [ ] Citation provenance is distinguished from build provenance
- [ ] Missing gates or irreproducible outputs receive focused tickets

## Progress

Determinism probes completed for MAP pages, indexes, global-map redirects, and representative timezone/locale conditions; the detailed evidence is summarized in `.memory/research/2026-09-16-architecture-deep-dives.md`. The deploy-path gate is now unblocked by #331; final architecture-claim reconciliation remains blocked by #342. Tickets #356–#358 capture the confirmed missing gates.

## Resolution

TBD
