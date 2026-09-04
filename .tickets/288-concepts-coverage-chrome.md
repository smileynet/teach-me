---
id: "288"
title: "Fix: check-topic-completeness --concepts extracts lesson chrome as concepts"
status: done
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

- [x] `check_concept_coverage` strips chrome (script/style/nav/header/footer + untagged `.lesson-meta`/`.page-nav` classes) before extraction — via the shared `tools/lib/html_prose.py::html_to_prose`
- [x] Re-run on the 7 #176 topics produces non-trivial, non-zero coverage reflecting real concept presence (was 0.0 everywhere → now 0.83–1.0; two topics show real 1-concept gaps)
- [x] No regression: `mise run verify` passes; 256 pytest pass; oracle still 100% on the #222 lesson
- [x] Coverage gaps reported are real authored concepts absent from prose, not chrome (`read win`/`min` gone)


## Resolution (2026-09-04) — Option A (chrome fix + metric realignment)

Investigation showed the ticket's premise was only half the cause. Two independent
problems made coverage 0.0 everywhere:
1. **Chrome leak** — `chunk_html` stripped semantic chrome (nav/header/footer) but the
   untagged `<div class="lesson-meta">` "Win:" statement + "~N min read" leaked in, so YAKE
   surfaced `read win`, `min` as "concepts."
2. **Vocabulary mismatch** — even chrome-clean, free YAKE extraction yields generic surface
   words (`files`, `Iceberg`, `AWS`) while the glossary keys are curated slugs
   (`manifest-file`, `partition-spec`). Measured overlap: 0/10. Chrome-strip ALONE still
   left coverage at ~0% — so the metric itself was measuring the wrong thing.

**Fix (both halves):**
- **Shared helper** `tools/lib/html_prose.py` (`strip_chrome_blocks` + `html_to_prose`,
  stdlib-only) — single source of truth for chrome removal, extended to drop untagged
  `.lesson-meta`/`.page-nav` by class. Repointed the two divergent copies at it:
  `hint-coverage-oracle.py` (dropped its local `strip_chrome`) and
  `chunk_text.py::chunk_html` (dropped its inline regex). 3 copies → 1 (SSoT, per the
  data-modeling lens).
- **Realigned metric** — `check_concept_coverage` now scores the lesson's OWN authored
  concepts (glossary-data keys + `data-term`/`<dfn>` spans): is each PRESENT in the teaching
  prose, and REINFORCED by an SR question? Hyphenated slug keys are split into words so
  `manifest-file` matches "manifest file" in prose; SR lookup mirrors `check_sr_questions`
  (topic file or `lesson_id` fallback). The coverage path no longer imports yake/networkx.

**Result (7 #176 topics):** coverage went from 0.0 everywhere to 0.83–1.0, with two topics
(triplanar 5/6, ink-flow 7/8) showing a real 1-concept gap (authored but under-explained) —
exactly the honest signal the metric should surface. iceberg reinforced 4 concepts via SR.

**Validation:** `mise run verify` EXIT 0; 256 pytest pass; oracle still 100% on 0015; help
text updated (no longer claims yake/networkx). Files: `tools/lib/html_prose.py` (new),
`tools/hint-coverage-oracle.py`, `tools/chunk_text.py`, `tools/check-topic-completeness.py`.
