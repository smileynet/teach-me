---
id: "373"
title: "Teach: generative-media-pipelines / model-onboarding-as-data"
status: open
blocked_by: ["367", "371"]
tags: ["content"]
---

# Teach: generative-media-pipelines / model-onboarding-as-data

Generate the lesson for topic 3 (MAP id `01M2R98N1JH2ACGN90N90CR7A3`, lesson file
`03-model-onboarding-as-data.html`, scope: **deep**, prereqs: the-universal-serving-pipeline).
Produced via the `generate-topic` pipeline.

> **Refined 2026-09-17** from a per-topic research+review subagent. Findings:
> `.scratch/research/373-refine.md`.

## What to build

Teach **ONE concept with THREE shapes**, not three case studies. Concept: *adding a model is a
config action, not new serving code — the model is data/config, the serving machinery is fixed.*
The learner's Win: "I can add a model as a config action and know which onboarding shape fits my
platform." The three shapes (with when-to-use criteria):

1. **Typed manifest in a registry** (REDACTED) — `ModelManifest` + `register_model()`
   as the only path; license gate enforced at registration.
2. **Catalog JSON + one universal data-driven handler** (REDACTED) — `model_registry.json` +
   one `inference.py` dispatching on env vars; format families; HF-direct-pull.
3. **Versioned workflow container** (REDACTED) — the ComfyUI+nodes+workflow-JSON image is the
   ECR-tagged unit; git→build→scan→approve→immutable-tag; vending Lambda gates.

**Load-bearing teachable — the rule of two:** build the generic seam only once two dissimilar
models need it. Only REDACTED ships explicit proof (CHORD PBR + TripoSR mesh, chosen
for max output-shape contrast). **State honestly** that REDACTED proves it implicitly (5 families,
one handler) and **REDACTED has DESIGNED but not PROVEN** a generic seam (Trellis2 is the only live
workflow; others staged) — don't imply otherwise.

Also: three runner strategies (native/comfyui/mock); **weights never baked** (S3→NVMe /
FSxN+FlexClone / HF-pull — the reason the onboarding unit stays small; cross-ref topic 2, don't
re-teach cold-start numbers); **governance-at-the-seam** for all three (license gate at
registration / HF gated-access pre-check + attribution / vending approval + team tag).

**Critical distinction to keep crisp:** onboarding-as-data ≠ multi-model endpoint (MME).
Onboarding-as-data = the model is *declared, not coded*; MME = many models *share one container's
memory*. REDACTED is onboarding-as-data WITHOUT shared-memory MME (each model = its own
scale-to-zero fleet). The noisy-neighbor / eviction-thrash warnings apply to the *shared-container*
variant — flag as a decision callout so learners don't conflate them.

## G2 warnings (Con callouts, cited)

Shared-container serving trades latency for generality (SageMaker MME: infrequent models pay
cold-start; high-TPS models still want dedicated endpoints); cold start **compounds** across a
config-composed pipeline; **noisy neighbor** is the shared-model tax (Salesforce shuffle-sharding
at 100K+ models); MME memory eviction thrash on an undersized instance; a catalog row with no
runnable handler/weights behind it is a dangling entry (studio guards with `conforms_to` +
`WeightsDecl` list).

## Prior art to cite (external convergence)

Reddit/DoorDash/Grab/Salesforce "model artifact + model config" platforms; SageMaker MME; Triton
model repository; HF custom handlers; model-registry pattern. All tagged `[L#]` in the findings file.

## Source-verification gate (per #367)

Every claim → repo file path (`contract.py`/`registry.py`/`bootstrap.py`; `model_registry.json`/
`inference.py`; `Dockerfile`/`workflow_api.json`/`vending/index.ts`) or `[L#]` external source. No
uncited claims; no invented manifest schemas (code blocks `data-mode="fragment"` unless a
downloadable final-state file ships per `code-validation-teaching.md`).

## Artifact set (authoritative gate: `tools/check-topic-completeness.py`)

Lesson HTML at **flat** `library/generative-media-pipelines/lessons/03-model-onboarding-as-data.html`;
reference; quiz (≥5/≥3); SR JSONL (≥1); **inline `glossary-data` block, not a JSON file**;
code-files dir only if `data-file` blocks exist. Follows `visual-teaching.md` +
`code-validation-teaching.md`.

## Acceptance criteria

- [ ] `library/generative-media-pipelines/lessons/03-model-onboarding-as-data.html` generated via `generate-topic` (flat path)
- [ ] The ONE concept stated + the three shapes presented with a *when-to-use-which* decision callout; per-platform citation table maps each onboarding claim to an exact repo file path
- [ ] Rule-of-two taught with the CHORD+TripoSR proof; stated honestly that REDACTED designed-but-not-proven a generic seam
- [ ] Onboarding-as-data distinguished from shared-container multi-model serving (decision callout); the shared-container G2 warnings carried with sources
- [ ] Governance-at-the-seam shown for all three (license gate / HF gated pre-check + attribution / vending approval + team tag)
- [ ] Reference + quiz (≥5/≥3) + SR JSONL + inline glossary produced; every claim cites a repo path or `[L#]`; near-transfer misconception-probe exercise (building the generic seam before a second dissimilar model exists)
- [ ] `mise run verify` passes AND `check-topic-completeness.py --workspace library/generative-media-pipelines --topic model-onboarding-as-data` (and `--concepts`) clean
