---
id: "334"
title: "Run the tests ingest suite inside verify"
status: open
priority: medium
blocked_by: []
type: fix
tags: ["arch-review"]
---

# Run the tests/ ingest suite inside verify

## Why

The `tests/` directory holds 12 pytest files covering the whole ingest pipeline (test_ingest_source, test_enrich_from_source, test_map_from_chunks, test_map_from_deps, test_classify_document, test_extract_concepts, test_concept_hints, test_enrich_prereqs, test_match_section, ...) — but no gate runs them. `verify` executes only `tools/test_map_page.py` and `tools/test_map_parser.py` (`mise.toml:135`), and pre-commit runs only `mise run verify`. AGENTS.md's testing posture says maintained tests exist for multi-consumer libraries like the ingest pipeline — right now they can silently rot.

## What to build

- Add the `tests/` suite to verify's pytest step (e.g. `uv run python -m pytest tests tools/test_map_page.py tools/test_map_parser.py -q`)
- Triage any failures honestly: fix, or descope a broken test with a documented reason (do not delete to go green)

## Acceptance criteria

- [ ] `mise run verify` runs the tests/ suite; output shows the full collected count
- [ ] All tests pass, or every failure is triaged (fixed or explicitly excluded with a reason in this ticket)
- [ ] Pre-commit hook still completes in reasonable time (spot-check duration before/after)

## Resolution

TBD
