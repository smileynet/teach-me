# Reference Study: coding-best-practices

## Summary

A **knowledge wiki** that synthesizes coding best practices from 17 programming books into a cross-referenced, source-attributed knowledge base. It processes books (PDFs/EPUBs) through an ingestion pipeline, extracts concepts/practices/antipatterns, and organizes them into a structured wiki with Obsidian wikilinks. Additionally, it encodes 16 author personas as AI agents that can review code, discuss design, or teach — each grounded exclusively in their documented book positions.

It is NOT a tutorial or blog — it's a queryable reference graph designed for rapid lookup, cross-source comparison, and conflict surfacing.

## Content Structure

### Directory Layout

```
books/           — Immutable source PDFs/EPUBs (never modified)
sources/         — Extracted markdown chapters (generated, gitignored)
intake/          — Raw source material + intake manifests (provenance tracking)
wiki/
  ├── books/       — One summary page per book (core thesis, key concepts, chapter guide)
  ├── authors/     — Author bio + methodology + distinctive vocabulary + blind spots
  ├── concepts/    — Cross-referenced concept pages (descriptive, not prescriptive)
  ├── practices/   — Actionable best practices (prescriptive: rule + how + when to break)
  ├── antipatterns/ — Named failure modes (description + recognition + remediation)
  └── syntheses/   — Cross-book analyses (agreements, tensions, divergences)
scripts/         — Extraction, linting, indexing, migration scripts
omp-book-reviewers/ — Portable persona skill package
.claude/agents/  — Generated agent definitions (one per author)
```

### Page Type Hierarchy

The wiki has a strict 6-type taxonomy:
1. **Book** — source of truth per book (immutable reference)
2. **Author** — methodology + vocabulary + blind spots per author
3. **Concept** — descriptive idea pages, multi-source perspectives
4. **Practice** — prescriptive actionable pages (Rule → How → When to Break)
5. **Antipattern** — named failure modes (Symptoms → Why Harmful → Fix)
6. **Synthesis** — cross-book meta-analyses (Agreements → Divergences → Practical Guidance)

### Cross-Referencing System

- Obsidian `[[wikilinks]]` throughout — every concept, practice, antipattern linked on first mention per section
- Each page has YAML frontmatter with `sources:` field linking back to book pages
- Bidirectional: concepts link to practices, practices link to antipatterns, all link to sources
- `index.md` — auto-generated catalog of all pages (by type, alphabetical)
- `link-sweep.py` — script that finds unlinked prose mentions and inserts missing backlinks
- `graph-stats.py` — reports connectivity metrics, hub pages, structural gaps

### The Compounding Pattern

Every new source doesn't just add pages — it enriches existing ones:
- Existing concept pages get a "Per [[new-source]]…" subsection
- Existing practices get new source attribution
- Syntheses are triggered when 3+ sources address a theme or 2 sources contradict

## Novel Patterns

### 1. Conflict-First Synthesis Design

The wiki explicitly **flags conflicts as first-class content**, not problems to solve:
- `> [!conflict]` callout syntax for unresolved disagreements
- "Points of Tension" synthesis with 10 named tensions between sources
- "Universal Agreements" synthesis identifying what 12+ of 16 books converge on
- Rule: "Silent resolution — choosing one and omitting the other — is data loss"

**teach-me doesn't do this.** Our lessons present one perspective per topic. We don't systematically surface where authorities disagree or treat disagreement as pedagogically valuable.

### 2. Author-as-Agent Personas

Each author is encoded as a constrained AI agent:
- Grounded exclusively in documented positions from their book
- Explicit "You Defer To" section limiting cross-references
- Anti-sycophancy constraint: "you MUST NOT soften your position"
- Scope boundaries: "Do not count method lines" (that's Clausen's domain)
- Discussion output in first person with documented positions only

**Novel for teach-me:** The "teach from multiple perspectives" model — same code reviewed through 3-5 different analytical frameworks simultaneously.

### 3. Situation Index (Symptom → Practice Routing)

`wiki/syntheses/situation-index.md` inverts the normal lookup direction:
- Start from observable symptoms ("A method requires scrolling to read")
- Route to a small cluster of relevant practice/concept pages
- Labels biased toward what agents can detect from code/tests/logs

**teach-me doesn't do this.** We organize by topic/subtopic. A "what's wrong here?" entry point for learners would be novel.

### 4. Structured Intake Pipeline with Provenance

Intake manifests (YAML) formally track:
- Exact pinned version (commit SHA, snapshot date)
- Derivation chain: intake → sources → wiki
- Separate commits for raw intake vs. derived interpretation
- Reproducibility: any derivation step can be re-run from manifests

### 5. Compound-Don't-Duplicate Principle

When a new source discusses an existing concept:
- DON'T create a second page
- DO add a subsection "As treated by [[New Source]]" to the existing page
- Deduplication check is mandatory in the ingestion workflow

**teach-me doesn't do this systematically.** Each lesson is standalone. Cross-referencing between topics is ad hoc.

### 6. Tag Vocabulary as Controlled Ontology

Tags drawn from a fixed, documented vocabulary only. Scripts validate compliance. New tags require updating the vocabulary section in AGENTS.md first.

### 7. Learning Path Syntheses

`wiki/syntheses/learning-path-*.md` — synthesized reading orders grouped by goal (fundamentals, FP, problem-solving, software design, systems programming). Not just "read these books" but which concepts from each book in what order.

## Applicable Insights for 'Teach from Docs' Feature

### 1. Source → Wiki Separation is Key

The project maintains a strict pipeline: raw source → extracted chapters → structured wiki pages. Source material is immutable; the wiki layer is the interpretation layer. For "teach from docs," we should similarly separate:
- Raw documentation (immutable reference)
- Teaching interpretation (our lesson layer)
- Cross-reference graph (connections between concepts)

### 2. Multi-Source Attribution Model

Every claim traces to a source via wikilink. When teaching from docs, we should:
- Track which doc page supports each lesson claim
- When docs contradict (common across versions/vendors), flag it rather than silently picking one
- Let the learner see the provenance: "According to the AWS docs on X…"

### 3. The Practice Page Template is Excellent

The practice page structure is highly applicable:
- **Rule** — one-sentence imperative
- **Why It Matters** — motivation
- **How to Apply** — concrete steps
- **When to Break It** — exceptions (crucial for real-world use)
- **Signals You Need This** — recognition patterns

This is more actionable than our current lesson format, which mixes explanation and action.

### 4. Synthesis Triggers

Automatically trigger cross-doc synthesis when:
- 3+ docs address the same concept differently
- 2 docs contradict on a meaningful point
- A concept appears with different vocabulary across sources

### 5. Situation-Based Entry Points

Instead of only topic-hierarchical navigation, offer:
- "I'm seeing X problem" → route to relevant lessons
- Observable symptoms as entry points to learning paths
- Diagnostic approach: what you see → what to learn

### 6. Persona-Based Teaching

The `/teach-with <author> <code>` command is directly applicable:
- "Teach me about X from the perspective of [framework/methodology]"
- Same concept explained through different lenses for different learning styles
- Each "perspective" grounded in specific source documentation

## How It Handles Transforming Source Material into Usable Knowledge

### Pipeline

1. **Extraction** — `split-chapters.py` breaks books into per-chapter markdown via pandoc/pdftotext
2. **Ingestion** — Agent reads chapters, creates book/author/concept/practice/antipattern pages following strict templates
3. **Deduplication** — existing concepts get new source subsections rather than new pages
4. **Cross-linking** — `link-sweep.py` inserts missing wikilinks and backlinks
5. **Synthesis** — when enough sources cover a theme, create synthesis pages comparing positions
6. **Validation** — `wiki-lint.py` checks broken links, missing frontmatter, invalid tags, orphaned pages, slop words
7. **Index maintenance** — `generate-index.py` rebuilds the master catalog

### Key Design Decisions

- **Never summarize without attribution** — every claim has a source wikilink
- **Preserve disagreement** — conflicts are content, not bugs
- **Strict schema** — all pages conform to typed templates (enforced by lint)
- **Compound over duplicate** — one canonical page per concept, enriched by multiple sources
- **Graph-first** — value is in the connections (wikilinks), not individual pages
- **Observable metrics** — `graph-stats.py` reports connectivity, hub detection, coverage gaps

### Quality Enforcement

- `wiki-lint.py` — structural validation (frontmatter, links, tags, sections)
- `link-sweep.py` — connectivity enforcement (missing links and backlinks)
- `graph-stats.py --gaps` — coverage gap detection
- `wiki-migrate.py` — schema version migration
- STYLE.md — prose quality rules (banned filler, slop words, self-referential narration)
- Anti-sycophancy rules in agent personas

## Key Takeaways for teach-me

1. **Conflict is pedagogically valuable** — when sources disagree, that IS the lesson
2. **Observable symptoms beat category hierarchies** for practical lookup
3. **Strict templates produce consistency** — the practice page template (Rule/Why/How/When-to-Break/Signals) is superior to freeform lessons
4. **Source provenance must be structural** — frontmatter `sources:` field, not inline mentions only
5. **Compound, don't duplicate** — existing topic pages should grow with new sources, not proliferate
6. **The wiki graph IS the product** — individual pages are less valuable than their connections
7. **Author-perspective diversity** — same concept through different frameworks deepens understanding more than one "correct" explanation
