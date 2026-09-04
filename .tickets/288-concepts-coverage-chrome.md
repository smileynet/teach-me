---
id: "288"
title: "Fix: check-topic-completeness --concepts extracts lesson chrome as concepts"
status: open
blocked_by: []
priority: medium
tags: [content-quality, tooling]
---

# Fix: check-topic-completeness --concepts extracts lesson chrome as concepts

## Problem

Surfaced by #176's coverage-report run (2026-09-03). `check-topic-completeness.py
--concepts` calls `extract_concepts_from_html(lesson_path, top_n=10)` on the ENTIRE
lesson HTML — including chrome (nav breadcrumb, the "Read the Win" statement, read-time
meta, script/style blocks). YAKE then surfaces boilerplate phrases as the top concepts:
`read win`, `win`, `min`, `godot toon`, plus high-frequency single words (`Iceberg`,
`files`, `AWS`). Those never match the multi-word glossary terms, so **every topic in
every domain reports `concept_coverage: 0.0`** regardless of lesson quality.

Verified across 7 topics in 3 domains (godot-gamedev, iceberg, ink-godot): 0.0 coverage
everywhere. Direct check on `0001-iceberg-metadata-tree.html` confirmed the top-10 extracted
concepts are `Iceberg / files / Apache Iceberg / read Win / ...` — chrome + generic words,
not the domain terms the lesson actually teaches.

The coverage% is therefore an unreliable signal today. (The hint-GENERATION side,
`concept_hints.py` #286, is unaffected and strong — this is only the coverage-CHECK path.)

## What to build

Strip chrome before extraction in `check_concept_coverage` (tools/check-topic-completeness.py,
~line 127). Reuse the already-shipped `strip_chrome()` in `tools/hint-coverage-oracle.py`
(#176) — it removes script/style/nav/header/footer before matching. Consider also biasing
toward the lesson's own multi-word glossary terms rather than raw global-frequency singles.

Cross-check: the #176 `hint-coverage-oracle.py` is the "did the lesson use its concepts"
direction (hints IN → taught?). This ticket fixes the complementary direction (concepts
extracted FROM the lesson → in the glossary?). Prefer the oracle until this lands.

## Acceptance criteria

- [ ] `check_concept_coverage` strips chrome (script/style/nav/header/footer + meta) before extraction
- [ ] Re-run on the 7 #176 topics produces non-trivial, non-zero coverage that reflects real glossary overlap (not `read win`/`min` boilerplate)
- [ ] No regression: `mise run verify` passes
- [ ] Coverage gaps reported are real domain terms, not chrome
