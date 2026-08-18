# Cross-Cutting Synthesis: Source-Based Learning Pipeline

## 1. Reinforcing Patterns (Convergence Across Research Areas)

### A. "Provenance Chain" + "Could They Answer This?" + "Source Fidelity"

The strongest convergence: **provenance tracking**, **source fidelity**, and **chunking strategies** all demand that generated artifacts trace to specific source passages.

- Provenance tracking establishes the chain: `source quote → objective → bloom level → question`
- Source fidelity requires preserving the source's core claims faithfully, only adding scaffolding around them
- Chunking strategies align chunk boundaries with learning objectives — each chunk becomes the traceable unit

**The unified principle:** A lesson chunk = a teachable unit with 2-4 objectives, each objective anchored to a source passage. Questions test only what the source teaches. Every generated artifact carries metadata pointing back to its source passage.

### B. "Cognitive Load Separation" + "Chunking (Pedagogical Normalization)" + "Elaboration Theory"

Three research streams agree on the same sequencing pattern:

- Cognitive load separation: teach the clean rule first, defer exceptions to review phase
- Chunking: each lesson introduces 2-4 concepts max, respects working memory limits
- Elaboration Theory (from source fidelity + chunking): epitome → elaborations → exceptions → synthesis

**The unified principle:** Each lesson presents ONE clean mental model (the happy path). Best practices, edge cases, and "in production you'd also..." content are separate artifacts surfaced during spaced repetition review, not in the initial lesson.

### C. "Multi-Source Synthesis" + "Compounding Pattern" + "Provenance Attribution"

When multiple sources exist for a concept:

- Multi-source synthesis: conflict is pedagogically valuable content, not a bug to resolve silently
- Coding-best-practices reference: compound-don't-duplicate — one canonical page per concept, enriched by each new source
- Provenance tracking: attribution must be per-claim, not per-document

**The unified principle:** A concept has ONE canonical representation in the system. New sources compound into it. Agreements strengthen; conflicts become first-class `[!conflict]` callouts with attribution. The learner sees both the resolved guidance AND the underlying disagreement.

### D. "Rustacean Academy Three-Phase Pipeline" + "Source → Wiki Separation"

Both reference projects maintain strict separation between source material and teaching interpretation:

- Rustacean Academy: `source/` (immutable raw) → `lessons/` (faithful reproduction) → `questions/` (derived with provenance)
- Coding-best-practices: `books/` (immutable PDFs) → `sources/` (extracted chapters) → `wiki/` (structured interpretation)

**The unified principle:** Raw source is immutable. Teaching artifacts are a separate layer that references back to source. This enables diffing, re-validation, and trust ("is this still what the source says?").

### E. "Durability Check" + "Cognitive Load Separation Level 2"

Both the Rustacean Academy's "Would they look this up in an IDE?" gate and cognitive load separation's "defer syntax to review" converge:

- Don't quiz on trivia retrievable from tooling
- Don't teach lookup-level facts in the lesson — they belong in the reference doc
- Quiz on mental models, explain-to-someone questions, and structural understanding

**The unified principle:** Lessons teach concepts and mental models. Reference docs hold lookup facts. SR cards test understanding, not recall. The three artifact types serve different cognitive functions.

---

## 2. Tensions and Conflicts

### A. Source Fidelity vs. Cognitive Load Separation

**Tension:** Source fidelity says "preserve the source's structure and qualifiers." Cognitive load separation says "strip away exceptions and present the clean rule first."

**Resolution:** These apply at different layers:
- **Fidelity** applies to the *reference doc* layer — preserve the source faithfully there
- **Cognitive load** applies to the *lesson* layer — simplify for initial teaching
- The lesson signals what it omits: "We're teaching the happy path here. For the full picture including edge cases, see the reference doc."

This is exactly the "annotated source" position on the fidelity spectrum — preserve source content's core claims, add scaffolding, signal where you've simplified.

### B. Compounding (One Page Per Concept) vs. Lesson Linearity

**Tension:** The compounding pattern says concepts should accumulate knowledge from multiple sources on a single page. But lessons are designed as linear progressions through a topic map.

**Resolution:** Separate the concept layer from the lesson layer:
- **Lessons** = linear, one-read-through artifacts optimized for initial learning
- **Reference docs** = compounding, concept-per-page artifacts that grow over time
- Lessons LINK to reference docs but don't duplicate them

teach-me already has this split (lessons/ vs reference/). The compounding pattern applies to the reference layer, not the lesson layer.

### C. Multi-Source Conflict Surfacing vs. Novice Cognitive Load

**Tension:** Multi-source synthesis research says surfacing conflicts develops critical thinking. Cognitive load research says novices can't handle conflicting information before base schemas stabilize.

**Resolution:** Gate by proficiency level:
- **During initial lesson:** Present one coherent path (resolve conflicts behind the scenes)
- **During SR review (L1 stable):** Introduce "there's another perspective..." as L2 cards
- **During mastery phase (L2 stable):** Full conflict surfacing with `[!conflict]` callouts

This maps to Elaboration Theory levels: epitome (one view) → elaboration (alternatives exist) → deep dive (full controversy).

### D. Chunking Size vs. Self-Containment

**Tension:** Chunking research says 800-2000 words / 5-12 minutes per lesson. Self-containment (Rustacean Academy) says each lesson must be readable without referencing other files, which may require pulling forward prerequisite context that inflates size.

**Resolution:** Use the "recap opener" pattern rather than full prerequisite inclusion:
- 2-3 sentence recap references prior concepts by name without re-explaining
- Prerequisites section with links (not content) for those who need refresh
- This keeps lessons within size budget while maintaining navigability

### E. Provenance Granularity vs. Generation Overhead

**Tension:** Provenance tracking wants passage-level source quotes for every question. This requires the generation pipeline to extract and store specific quotes alongside each generated question — significant additional complexity.

**Resolution:** Two-tier provenance:
- **Lesson generation:** Section-level provenance (which source section informed which lesson section) — lower overhead, still auditable
- **Question generation:** Passage-level provenance (exact quote that teaches what the question tests) — higher overhead, but questions are fewer and higher-stakes

The "Could They Answer This?" gate only applies to questions, not to every sentence in a lesson.

---

## 3. Recommended Architecture

### Pipeline Overview

```
SOURCE INGESTION           LESSON GENERATION          POST-PROCESSING
─────────────────          ─────────────────          ───────────────

[Raw source]               [Lesson]                   [Jargon annotated]
    │                          │                           │
    ▼                          ▼                           ▼
[Chunked source]           [Reference doc]            [Questions + provenance]
    │                          │                           │
    ▼                          ▼                           ▼
[Source manifest]          [Diagram scaffolding]      [SR cards (L1/L2/L3)]
```

### Layer Separation

| Layer | Purpose | Mutability | Provenance |
|-------|---------|------------|------------|
| `source/` | Raw ingested material | Immutable after capture | URL + date + version |
| `source-chunks/` | Pedagogically-chunked segments | Regenerable from source/ | Chunk → source section mapping |
| `lessons/` | Teaching artifacts (clean mental models) | Authored/generated | Lesson section → source chunk |
| `reference/` | Lookup-optimized concept pages | Compounds over time | Per-claim source attribution |
| `questions/` | SR cards with provenance | Generated + validated | Passage-level `source_quote` |

### Data Flow

1. **Ingest:** Raw source captured to `source/`. Manifest records URL, date, version.
2. **Chunk:** Hybrid pipeline (structural split → pedagogical normalization → context injection) produces `source-chunks/` with 800-2000 word segments, 2-4 objectives each.
3. **Generate lesson:** From chunks, produce a lesson HTML teaching the clean mental model. Diagrams added. Best practices EXCLUDED (they go to L2 cards later).
4. **Generate reference:** From the same chunks, produce a reference doc preserving source structure more faithfully. This is where source fidelity lives.
5. **Generate questions:** From lesson content (not source directly), produce SR cards with passage-level provenance. Apply "Could They Answer This?" gate.
6. **Stratify questions:** Tag each card L1 (base concept recall/explanation), L2 (exceptions/best practices/alternatives), or L3 (production tradeoffs/cross-cutting synthesis).
7. **Post-process:** Jargon annotation, SVG color check, link validation.
8. **Verify:** Check completeness (all chunks covered), provenance validity (source quotes still exist), and SR gate (every question answerable from lesson content).

---

## 4. Concrete Implementation Decisions

### Decision 1: Adopt the hybrid chunking pipeline for source ingestion

**What:** When ingesting external content, apply three stages: structural split at headings → pedagogical normalization (800-2000 words, 2-4 objectives per chunk) → context injection (breadcrumb prefix + recap).

**Rationale:** Chunking research shows this outperforms both pure structural and pure semantic approaches. The 800-2000 word / 5-12 minute target is well-supported by edX engagement data and cognitive load theory (3-4 novel elements in working memory).

**Concrete format:** Each source chunk gets a metadata header:
```yaml
---
source: source/aws-docs/persistence.md
section: "Append-Only File"
word_count: 1247
objectives:
  - "Explain how AOF provides durability"
  - "Compare AOF vs RDB trade-offs"
breadcrumb: "Redis > Persistence > AOF"
---
```

### Decision 2: Separate lessons from reference docs with different fidelity targets

**What:** Lessons target "annotated source" on the fidelity spectrum (simplified for learning, with added diagrams/analogies). Reference docs target "faithful paraphrase" (preserving structure, qualifiers, and terminology of the source).

**Rationale:** Source fidelity research shows these serve different needs. Lessons serve initial comprehension (where going beyond the source is warranted). Reference docs serve lookup and exam prep (where fidelity to source vocabulary matters). teach-me already has this split — formalize the different fidelity targets.

### Decision 3: Implement passage-level provenance for SR questions

**What:** Extend the JSONL question format with `source_lesson`, `source_section`, `source_quote`, and `derivation` fields.

**Rationale:** The "Could They Answer This?" gate requires knowing exactly what passage teaches what the question tests. This enables: (a) validation that questions are answerable, (b) showing the learner WHERE to re-read on failure, (c) invalidation when lessons change.

**Format:**
```jsonl
{
  "id": "q-redis-aof-01",
  "question": "Explain to a colleague why AOF provides stronger durability guarantees than RDB snapshots.",
  "source_lesson": "lessons/03-persistence/index.html",
  "source_section": "append-only-file",
  "source_quote": "AOF logs every write operation received by the server",
  "derivation": "direct",
  "level": 1
}
```

### Decision 4: Stratify SR cards into L1/L2/L3 with proficiency gating

**What:** Tag every SR card with a cognitive level:
- **L1:** Base concept explanation ("Explain how X works")
- **L2:** Exceptions, best practices, alternatives ("When would X not apply?")
- **L3:** Production tradeoffs, cross-cutting synthesis ("Compare X vs Y across contexts")

L2 cards are only introduced after L1 cards for the same topic reach stable intervals (4+ days). L3 after L2 stable (14+ days).

**Rationale:** Cognitive load separation research (Heffernan et al. 2021) directly demonstrates that exception accuracy improves significantly when exceptions are introduced AFTER rule consolidation. The hippocampal encoding study showed delayed-exception accuracy was significantly above chance (β=0.732, P<0.001) while early-exception accuracy was NOT (β=0.132, P=0.272).

### Decision 5: Use `[!conflict]` callouts in reference docs, not lessons

**What:** When sources disagree, reference docs show the conflict with attribution. Lessons present the resolved practical guidance without the controversy.

**Rationale:** Multi-source synthesis research says conflict is pedagogically valuable — but cognitive load research says not during initial schema formation. Resolution: conflicts live in reference docs (consulted after initial learning) and surface as L2/L3 SR cards after base schema stabilizes.

**Exception:** When the conflict IS the lesson (e.g., "SQL vs NoSQL trade-offs"), surface it in the lesson with structured comparison, not as an afterthought.

### Decision 6: Source preservation with manifest tracking

**What:** When deriving lessons from external sources, store the raw source in a `source/` directory with a manifest file recording URL, access date, and version. The source is immutable after capture.

**Rationale:** Both reference projects (Rustacean Academy, coding-best-practices) independently arrived at this pattern. It enables: diffing lessons against source for drift detection, re-generation when the pipeline improves, and trust that the source hasn't been subtly altered.

**Format:**
```yaml
# source/manifest.yaml
- id: aws-redis-persistence
  url: https://redis.io/docs/management/persistence/
  captured: 2026-08-17
  version: "Redis 7.2 docs"
  format: markdown
  file: aws-docs/persistence.md
```

### Decision 7: Provenance signals in lesson HTML

**What:** Lessons visually distinguish source-derived content from teacher additions (analogies, diagrams, examples) using CSS classes and callout patterns.

**Rationale:** Source fidelity research identifies this as critical for learner trust and error correction. When an analogy breaks down, the learner needs to know it wasn't "official" source content. Implementation: `<aside class="teacher-note">` for analogies/scaffolding, with a subtle visual indicator (lighter background, "Think of it like..." framing).

---

## 5. Build Now vs. Defer

### Build Now (ticket 135 scope)

| Item | Rationale |
|------|-----------|
| Source manifest format + storage convention | Foundation everything else builds on. Low effort, high leverage. |
| JSONL provenance fields (`source_lesson`, `source_section`, `source_quote`, `derivation`, `level`) | Required for the "Could They Answer This?" gate. Without this, questions can't be validated. |
| L1/L2/L3 card stratification in the generate-topic pipeline | Core architectural decision. Affects every future topic generation. Straightforward to add to the existing JSONL format. |
| Proficiency gating logic in SR scheduler | The SR system already tracks intervals. Adding a "don't surface L2 until L1 stable" check is a small extension. |
| Lesson/reference fidelity split convention (documented in skill) | Zero code — just a documented guideline in the teach skill that lesson generation follows "annotated source" fidelity and reference docs follow "faithful paraphrase." |
| Hybrid chunking heuristic for source ingestion | Core to the "teach from docs" feature. Without this, source material is processed ad hoc. |

### Defer (future tickets)

| Item | Why defer | Prerequisite |
|------|-----------|--------------|
| Automated conflict detection between sources | Complex ML task (ConflictRAG-style). Few topics currently have multiple sources. | Multi-source teaching scenarios in production |
| Compounding reference docs (wiki-style accumulation) | Requires a concept-identity system (recognizing "same concept" across topics). Over-engineering for current scope. | Multiple topics covering overlapping concepts |
| Situation-based entry points ("I'm seeing X problem") | Requires a symptom → concept routing layer. Novel UX work. | Substantial lesson corpus to route into |
| `[!conflict]` UI components in reference docs | Need actual multi-source conflicts to display first. | Multi-source topic generation |
| Author-perspective personas for multi-lens teaching | High complexity, unclear value until we have multi-source content. | Compounding reference docs |
| Automated provenance re-validation on lesson edit | Requires diffing infrastructure. Low urgency (lessons don't change often). | Provenance fields in production |
| Source diff/drift detection (source updated upstream) | Nice-to-have but sources rarely change mid-learning. | Source manifests in production for 3+ months |
| Progressive disclosure conflict panels in HTML | DOM complexity for a niche case. Build when we have conflicts to show. | `[!conflict]` content exists |
| Adaptive chunking by learner cognitive state | Research question, not engineering task. No system does this well yet. | Baseline chunking working + learner state signals |

### Sequencing for Deferred Items

```
Now (ticket 135):
  Source manifest + provenance fields + L1/L2/L3 + proficiency gating + chunking

Next (when multi-source teaching is needed):
  Compounding reference docs + [!conflict] callouts + conflict detection

Later (maturity features):
  Situation index + author personas + adaptive chunking + drift detection
```

---

## Summary

The research converges on a clear architecture: **source → chunk → lesson/reference/questions** with strict provenance, cognitive load gating, and layer separation. The key insight is that teach-me already has most of the structural scaffolding (lessons/ + reference/ + SR cards) — what's missing is:

1. **Formal provenance** (questions → source passages)
2. **Cognitive level stratification** (L1/L2/L3 with gating)
3. **Systematic chunking** for source ingestion
4. **Fidelity conventions** distinguishing lesson-layer freedom from reference-layer faithfulness

These four additions transform the pipeline from "generate lessons about a topic" to "derive verifiable teaching artifacts from source material with appropriate fidelity and sequencing."
