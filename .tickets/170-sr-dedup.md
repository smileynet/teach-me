---
id: "170"
title: "Feature: SR question deduplication via TF-IDF similarity"
status: open
blocked_by: ["141"]
priority: low
tags: [platform]
---

# Feature: SR question deduplication via TF-IDF similarity

## What to build

Add a `--dedup` flag to `sr-check.py` that detects semantically duplicate SR questions within
a domain, using TF-IDF cosine similarity (the infra from `enrich_from_source` / spike #161) on
card prompts + expected answers. Report-only (never mutates cards). ~30 LOC.

(#171 was filed as a duplicate of this and "closed as duplicate" with its ACs unchecked — the
real, unbuilt work lives here. Body specified from #171.)

## Acceptance criteria

- [ ] `mise run sr:check -- --dedup` reports card pairs with cosine similarity > 0.5
- [ ] Output includes both card prompts, the similarity score, and source file
- [ ] Does not modify cards — report only (user decides which to suspend)
- [ ] Works across all domains in the workspace

## Validation

- [ ] Two near-duplicate cards → detected
- [ ] Two unrelated cards → not flagged
- [ ] `mise run sr:check` without `--dedup` still works as before

## Context

Verified NOT implemented (2026-09-04, #285 triage): `tools/sr-check.py` has no `--dedup` flag
and no cosine/TF-IDF code on the SR path (the only dedup in-repo is unrelated concept-name
dedup in `concept_hints.py`). Multi-source enrichment (#141) can create semantic duplicates
when two sources cover the same concept; no dedup exists today, so duplicate cards waste review
time. TF-IDF + cosine is already installed/validated (spike #161). Kept OPEN as real backlog
(low priority) — the stub body is now populated so it no longer reads as a template placeholder.
