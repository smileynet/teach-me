---
id: "171"
title: "Feature: SR question deduplication via TF-IDF similarity"
status: done
blocked_by: []
priority: low
---

# Feature: SR question deduplication via TF-IDF similarity

> **Closed as duplicate of #170.**

## What to build

Add `--dedup` flag to `sr-check.py` that detects semantically duplicate SR questions within a domain. Uses TF-IDF cosine similarity (from enrich_from_source infrastructure) on card prompts + expected answers.

## Context

- Multi-source enrichment (#141) can create semantic duplicates when two sources cover the same concept
- No deduplication exists today — duplicate cards waste review time
- TF-IDF + cosine similarity is already installed and validated (spike #161)
- ~30 lines of new code in `tools/sr-check.py`

## Acceptance criteria

- [ ] `mise run sr:check -- --dedup` reports card pairs with cosine similarity >0.5
- [ ] Output includes: both card prompts, similarity score, source file
- [ ] Does not modify cards — report only (user decides which to suspend)
- [ ] Works across all domains in the workspace

## Validation

- [ ] Create two near-duplicate cards → detected
- [ ] Two unrelated cards → not flagged
- [ ] `mise run sr:check` without --dedup still works as before
