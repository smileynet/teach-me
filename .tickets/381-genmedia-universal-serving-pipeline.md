---
id: "381"
title: "Teach: generative-media-pipelines / the-universal-serving-pipeline"
status: done
blocked_by: ["367"]
tags: ["content"]
---

# Teach: generative-media-pipelines / the-universal-serving-pipeline

Generate the lesson for topic 1 of the `generative-media-pipelines` domain (MAP id
`01M2R98N1JTYQXWXSDV3EBC7MW`, lesson file `01-the-universal-serving-pipeline.html`, scope:
substantial, prereqs: none). Produced via the `generate-topic` pipeline (research → generate →
post-process → verify) — do not hand-author around it.

> **Refined 2026-09-17** from 4 dispatched subagents (2 external research: serving-pipeline
> architecture + diagram pedagogy; 2 internal review: design-source fidelity + lesson-authoring
> contract). Findings: `.scratch/research/371-*.md`.

## What to build

Teach the **9-stage canonical loop** shared by all three explored platforms, as a single diagram
the three platforms map onto so the shared shape *and* the divergences are visible:

```
client → auth → submit → queue → scale-to-zero GPU worker → weight staging → infer → output store → progress stream
```

This is the pinned form (repeated verbatim in the MAP orientation, MAP topic-1 `why`, MISSION
success bullet, and the study guide Part 2). **Do NOT reproduce the study guide's compressed
one-liner** ("weights S3→local", Client/Auth fused) — it drops `auth` as a visible stage and looks
like an error. Frame the loop under its industry name — **Asynchronous Request-Reply /
Queue-Based Load Leveling** (return a job handle immediately → poll/stream → result) — so it
transfers to any stack `[L4:established]`.

Every later topic is "a decision inside this loop," so topic 1 lands the whole shape and defers the
depth.

## Diagram (per pedagogy + visual-teaching.md)

- Base diagram: `draw-diagram.py --type graph --backend graphviz --title "…"` — the loop has a
  back-edge (result/progress streams back to the caller), which `--type flow` (linear) can't
  express. `--title` auto-injects `role="img"` + `<title>` + `aria-labelledby` + viewBox-only.
- **5–9 element cap (hard rule).** The full 9-stage loop + 3 platform overlays exceeds one view.
  Teach a fixed **shared skeleton** (5–7 role-labelled stages) as the base, then **progressively
  layer** detail (retries/DLQ/autoscaling are zoom-ins on one stage, NOT base-view boxes). Show
  shared-vs-divergent with a consistent signaling cue (color/dashed) on the parts that vary + a
  **companion pattern→instances mapping table** beside the diagram carrying the per-platform
  variance. Labels ON the nodes.
- A separate small **sequence diagram** may carry the async submit→poll/stream→result handshake
  (different question than the structural flow — don't merge them).

## Per-platform mapping (cite the stage→file-path table)

Map each platform onto the loop as columns/annotations on the SAME diagram. **Cite each
stage/platform cell with its own repo file path** — the table is prebuilt in
`.scratch/research/371-review-design-source.md` (the DCC service / the artist studio / the ComfyUI platform, one file
path per stage). Do not cite the loop generically.

Hang the divergences on the **six axes** (the source's own comparison structure):
serving substrate · target user/client · progress transport · queue · weight staging ·
scale-to-zero depth.

**Three asymmetries to represent honestly (do NOT flatten into a too-clean loop):**
1. the artist studio's Bedrock path has **no platform-owned worker/queue stage** — the managed service owns
   it; the worker box is "someone else's."
2. the artist studio's "auth" is **AWS-account trust, not a per-request authorizer** — don't invent a
   Cognito-style gate it lacks.
3. the ComfyUI platform's worker is a **warm-pod floor** (KEDA `minReplicaCount 1`, GPU cold start 3–4 min), **not
   literal zero** — the source explicitly corrects this.

## Scope boundary (defer to later topics)

Topic 1 is the **shape only**. Defer to their owning topics: SageMaker Async as the worked
reference + cold-start numbers → topic 2 (scale-to-zero); onboarding-as-data → topic 3;
weight-staging mechanics (S3→NVMe / FSxN+FlexClone / HF-pull) → topics 2/3; ComfyUI
one-process-one-workflow specifics → topic 5. State the general worker-pool rule
(concurrency = 1 per GPU) here; defer the ComfyUI instance.

## Source-verification gate (per #367)

- Every load-bearing claim traces to a **repo file path** (the three explored repos are primary)
  or a **`[L#:confidence]` external source** per `source-authority` steering. No parametric memory.
- Design source: the research notes (non-public, removed).
  Backing: the per-platform findings (non-public).
- External prior art available in `.scratch/research/371-external-serving-pipeline.md` (fal.ai
  run/subscribe/submit verbs + Queued/InProgress/Completed status model; AWS async reference
  arch; SSE-as-default-for-one-way-progress; the "autoscaler kills a job mid-generation",
  "broker ≠ result store", and "WebSocket-where-SSE-suffices" anti-patterns for a decision callout).

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

A completed topic must produce ALL of:
- **Lesson HTML** at `library/generative-media-pipelines/lessons/01-the-universal-serving-pipeline.html`
  (FLAT under `lessons/` — the checker globs `lessons/*.html` at ONE level; a nested
  `lessons/<domain>/` path is silently missed). Must pass `check_lesson_features`: SVG `role="img"`,
  inline `glossary-data` block + `.term` spans, lesson-actions.js, theme-toggle.js, `<details>`
  exercise, `var(--svg-*)` (no hardcoded hex).
- **Reference doc** at `reference/{slug}.html`.
- **Quiz** at `lessons/quiz/{slug}.html` — ≥5 cards, ≥3 card types.
- **SR questions** at `.user/learning-records/questions/generative-media-pipelines.jsonl` — ≥1 card
  for the topic (target 4–8 open + 2–3 interactive; per-user overlay, not committed).
- **Code files** at `reference/code/{slug}/` + README — ONLY if the lesson has `data-file` blocks.
- The **glossary is an inline `<script id="glossary-data">` block in the lesson HTML, NOT a separate
  JSON file.**

## Authoring rules that also apply (visual-teaching.md + code-validation-teaching.md)

Narrative code-block framing (lead-in/bridge/connect-back; no bare "Here's the code"); downloadable
+ real-toolchain-validated code files if any; callout "when to use which" decision criteria (e.g.
poll vs SSE vs WebSocket vs webhook — SSE is the correct default for one-way progress); glossary
coverage (each term explained in prose AND reinforced by an SR card; min 3 terms); WCAG SVG
accessibility + color-never-alone; 3+ cited source URLs; forward-link stitching (no prereq to
update — topic 1 is the root); prose-check subagent pass after authoring.

## Acceptance criteria

- [x] `library/generative-media-pipelines/lessons/01-the-universal-serving-pipeline.html` generated via `generate-topic` (FLAT path — verified against the checker's `lessons/*.html` glob)
- [x] Single shared-skeleton diagram (7-stage skeleton + dashed back-edge, hand-authored accessible inline SVG — see note), ≤9 elements in the base view, with the three platforms mapped in a companion variance table; deeper detail progressively layered
- [x] The three honest asymmetries represented (the artist studio no-worker / account-trust auth; the ComfyUI platform warm-pod floor) — loop not flattened
- [x] Divergences hung on the six axes; SageMaker Async + cold-start numbers deferred to topic 2
- [x] Reference doc + quiz (9 questions, 6 types) + SR JSONL (6 open + 3 interactive) + inline glossary produced
- [x] Every load-bearing claim cites a repo file path or `[L#]` source (each diagram cell uses its own stage→file-path citation)
- [x] `mise run verify` passes (exit 0). `check-topic-completeness --concepts` reports concepts 100% covered (5/5). NOTE: the completeness script's `has_lesson_actions`/`has_theme_toggle`/quiz-card-count checks are STALE — they grep for old script filenames and old quiz markup the current `page-shell.js` + Preact-quiz architecture replaced, so they false-negative on EVERY shipped lesson (gltf-format, godot-asset-pipeline fail identically). Not part of `mise run verify` (the CI gate). Filed as a follow-up.

> **Diagram-tooling note:** the ticket named `--type graph --backend graphviz`, but the system's graphviz is 2.44.0 and the tool requests the `svg_inline` format that needs graphviz ~7.x — a pre-existing environment gap. The loop diagram was hand-authored as an accessible inline SVG (matching the gltf-format house pattern of hand-drawn SVGs; `role="img"` + `<title>` + `aria-labelledby` + viewBox, `var(--svg-*)` only), which gives precise control over the 7-stage skeleton, the dashed back-edge, and the ON-node labels. The intent (a graph with a back-edge, not a linear flow) is satisfied.

## Resolution

Built topic 1 via the `generate-topic` pipeline (research → generate → post-process → verify). Research/context reused the 4 findings files from the 2026-09-17 refinement pass (`.scratch/research/371-*.md`); generate authored the four artifacts; post-process ran the SVG-var check + a dispatched prose-check subagent (3 priority fixes applied: triple-thesis restatement, triple GPU-rule restatement, em-dash density); verify ran the CI gate.

**Shipped:**
- `library/generative-media-pipelines/lessons/01-the-universal-serving-pipeline.html` — 9-stage loop taught as a hand-authored accessible SVG (7-stage skeleton + dashed back-edge, role-coded), per-platform stage→file-path citation table (all cells `[L1]` against the three repos), six divergence axes, three honest-asymmetry table, progress-transport decision callout (poll/SSE/WS/webhook, SSE default), two anti-patterns (autoscaler-kills-job, broker≠result-store), deferrals to topics 2/3/4/5, near-transfer misconception exercise, 5 inline glossary terms.
- `reference/01-the-universal-serving-pipeline.html` — scannable companion.
- `lessons/quiz/01-the-universal-serving-pipeline-quiz.html` — 9 questions, 6 types.
- `learning-records/questions/generative-media-pipelines.jsonl` — 6 open (explain/apply/predict, L1→L3) + 3 interactive (sequence/match/fill).
- Map page + aggregate index regenerated (idempotent — no diff).

**Verified:** `mise run verify` → exit 0 (verify-links, lint-html, check-maps-forest, check-index-drift, check-svg-vars, 72 pytest, 20 interactive checks, ink transcripts). Concepts 100% covered (5/5). Visual QA: loop SVG present + visible, 5 term spans, exercise details, 0 console errors. Diagram hand-authored due to a pre-existing graphviz-version gap (2.44.0 vs the `svg_inline` format's ~7.x requirement). The `check-topic-completeness` `has_lesson_actions`/`has_theme_toggle`/quiz-card checks false-negative on all shipped lessons (stale markup expectations) — not the CI gate; follow-up warranted.

Committed signed.
