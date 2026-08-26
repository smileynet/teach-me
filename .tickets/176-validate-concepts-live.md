---
id: "176"
title: "Validate: run concept hints + enrichment on all live workspace topics"
status: open
blocked_by: ["175"]
priority: high
tags: [source-ingest, content-quality]
---

# Validate: run concept hints + enrichment on all live workspace topics

## What to build

After #175 quality fixes land, run the full concept hints + enrichment pipeline against all live workspace topics to validate:
- Concept extraction produces useful domain terms (not noise)
- L-levels differentiate appropriately per domain
- Multi-source enrichment matches correctly where multiple sources exist
- Coverage checker identifies real gaps (not boilerplate mismatches)

### Domains to test

| Domain | Source | Topics | Expected outcome |
|--------|--------|--------|-----------------|
| blender-godot-shaders | Web research (7 lessons, no source-chunks) | 7 complete | Coverage check on existing lessons only |
| code-design | Ousterhout + Five Lines (21+29 chunks) | 20 topics, 2 lessons | Full pipeline: hints + enrichment + coverage |
| rust-fundamentals | Rust by Example + Rust Book (9+2 chunks) | 9 topics | Full pipeline on web-sourced content |

### Process

1. Run `concept_hints.py` on each domain with source-chunks → save all hint files
2. Run `check-topic-completeness.py --concepts --all` per workspace domain → report coverage
3. Manually review: are the top-5 concepts per topic actually the right ones?
4. Run enrichment overlay inspection: are matches sensible? Any false positives?
5. Generate one lesson using the hints (pick the highest-value unwritten topic) and confirm the skill uses them

## Acceptance criteria

- [ ] Concept hints generated for all 3 domains without errors
- [ ] Top-5 concepts per topic are domain-relevant (manual review, >80% useful)
- [ ] Coverage report produced for all topics with existing lessons
- [ ] At least one lesson generated using concept hints as input
- [ ] No regressions: `mise run verify` passes throughout

## Validation

- [ ] Manual spot-check: open 3 concept hint files, confirm terms are sensible
- [ ] Generated lesson uses L-levels from hints for SR questions
- [ ] Coverage gaps in the report lead to actionable improvements (not false alarms)
