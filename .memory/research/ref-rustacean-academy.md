# Reference Study: Rustacean Academy

## Summary

Rustacean Academy is a **Rust learning system derived from Rust by Example** (24 chapters, ~150 topics). It uses a multi-agent crew (ferris coordinator + 4 specialists) to deliver daily 15-30 minute sessions combining spaced repetition review, Socratic teaching, and compiler-evaluated exercises. Content is **derived from an existing written source** (Rust by Example), not generated from scratch — a deliberate architectural choice documented in ADR-001.

Key surfaces: CLI-based agent interactions (kiro-cli), a Rust/Axum web app with Tailwind CSS (dark-first), and Anki export. Uses SQLite for progress and SM-2 scheduling at both topic-level and individual card-level.

## Content Structure

### Three-Phase Pipeline: Capture → Extract → Generate

1. **Capture**: Faithfully reproduce source text into `curriculum/lessons/`. Only minor formatting changes allowed. Raw source preserved in `curriculum/source/` for diff verification.
2. **Extract**: Derive 3-7 learning objectives per topic from lesson content. Each objective has an observable Bloom's verb.
3. **Generate**: Create questions (1-2 per objective), flashcards (1 per atomic fact), and exercises (3 levels per topic) — all traceable to objectives and source quotes.

### Directory Layout

```
curriculum/
├── topics.md              # Chapter index
├── chapters/NN-slug.md    # Prerequisites, topics table, best practices, antipatterns, prior art
├── source/chNN/           # Raw unmodified source markdown
├── lessons/chNN/          # Faithful reproduction + pedagogical intros
├── objectives/chNN/       # Observable learning outcomes
├── questions/chNN.md      # Per-chapter Q&A with traceability
├── cards/chNN.md          # Flashcards (front/back with stable IDs)
├── exercises/chNN/        # Standalone .rs files (3 difficulty levels)
└── glossary.yaml          # Domain terms
```

### Naming

Topic IDs: dotted format `1.3.2` (chapter.topic.subtopic). Stable identifiers used in progress tracking, URL routing, and cross-references.

## Novel Patterns

### 1. Output-Based Exercise Evaluation (ADR-002)

Instead of `assert_eq!` + `todo!()` patterns, exercises start as working code with `// TODO` comments. Evaluation compares stdout against `// Expected output:` lines. Soft technique checks (`// Check contains:`, `// Check matches:`) nudge toward correct approach without hard-failing.

**Why it matters for teach-me**: Our exercises could adopt this pattern for any language with a REPL/compiler. It's more natural than test harness boilerplate.

### 2. Content Derivation with Provenance Chain

Every question traces: source quote → objective → bloom's level → Q/A. The `source:` field with an actual quote creates an auditable chain. Lessons diff against raw source to verify fidelity.

**Why it matters for teach-me**: When teaching from docs/books, this pattern ensures we never invent content beyond what the source teaches. The "Could They Answer This?" gate is a powerful quality check.

### 3. Cognitive Load Separation: Learning vs Review

Best practices and antipatterns are explicitly excluded from lesson content. They surface only during spaced repetition review, after the base concept is internalized. This is a deliberate pedagogical choice documented in the pipeline.

**Why it matters for teach-me**: Our lessons currently mix concept introduction with best practices. Separating these could reduce initial cognitive load.

### 4. Technique Checks (Dual Verification)

Exercises check both output correctness AND approach correctness. A student who clones everything to avoid borrowing gets told "Your code works, but you avoided the concept we're practicing."

**Why it matters for teach-me**: Our quiz-me skill focuses on recall. Adding technique verification to interactive exercises would catch "technically correct but missing the point" solutions.

### 5. Multi-Agent Crew with Clear Ownership Boundaries

| Agent | Owns | Never Does |
|-------|------|------------|
| ferris (coordinator) | Session orchestration, delegation | Teach, generate content |
| nautilus (teacher) | Capture, extract, generate questions/cards | Exercises, progress |
| lagoon (coach) | Generate exercises, guide practice | Lessons, progress |
| tide (tester) | Progress tracking, quizzes, SR scheduling | Content generation |
| jellyfish (reviewer) | Code review, compiler help | Content, progress |

Strict ownership prevents agents from stepping on each other. The coordinator never teaches directly.

### 6. Exercise File as Complete Specification

Each `.rs` exercise file is self-contained: title, goal, concepts link, expected output, hints (graduated), and technique checks — all in comments. The web backend parses these at runtime. No separate metadata files.

### 7. Learning Paths (3 predefined routes)

Three paths through the same 24-chapter curriculum based on background:
- Path A: Foundations First (beginners)
- Path B: Systems Programmer (from C/C++)
- Path C: Application Developer (from Python/JS)

Same material, different ordering. `curriculum.py next` uses the active path + progress to determine what's next.

### 8. Flashcard Format with Stable IDs

Cards use `@8-hex-chars` inline IDs that survive content edits. Format: `?` separates front/back, `---` separates cards. Simple, grep-friendly, parseable without YAML/JSON overhead.

### 9. `.skip_exercises` Marker Files

Topics that don't need exercises (e.g., "Hello World" — too trivial) have a `.skip_exercises` file listing topic IDs to skip. Coverage validation respects these.

### 10. Session Structure: 4 Mandatory Phases

Every daily session: Review (SR) → Learn (new topic) → Practice (exercises) → Wrap-up (record + preview). Phase gates prevent skipping practice. Phase 0 (content prep) runs silently before the student arrives.

## Applicable Insights for "Teach from Docs" Feature

1. **Source preservation + diffing**: When deriving lessons from docs, keep the raw source separately. Enables verification that the lesson faithfully represents the source.

2. **"Could They Answer This?" gate**: Every quiz question must trace to a specific passage in the source. If you can't point to where it's taught, delete the question.

3. **Durability check for questions**: Test concepts/mental models, not syntax trivia. "Would they look this up in an IDE?" → don't quiz on it.

4. **Progressive exercise levels**: Level 1 (isolated concept), Level 2 (richer context), Level 3 (concepts interacting). The student builds from safe isolation to integration.

5. **Pedagogical introductions**: Every lesson opens with a 2-3 sentence blockquote that states the problem solved, what the learner can do after, and connects to prior knowledge. Brief enough that code appears within 30 seconds of reading.

6. **Chapter metadata files**: Store best practices, antipatterns, and prior art (cross-language bridges) separately from lesson content. Surface them at the right time (review, not initial learning).

7. **Coverage validation scripts**: `curriculum.py coverage` and `curriculum.py objectives --gaps` detect missing content systematically. Essential when generating from a large source corpus.

8. **Self-containment rule**: Each lesson must be readable without referencing other lesson files. Pull forward prerequisite context rather than requiring cross-references.

## Key Differences from teach-me

| Dimension | teach-me | Rustacean Academy |
|-----------|----------|-------------------|
| **Content origin** | AI researches + generates original lessons | Derives from existing written source (Rust by Example) |
| **Scope** | Any topic (generalist) | Single domain (Rust) |
| **Delivery** | Static HTML files opened in browser | Live web app (Axum + SQLite + HTMX patterns) |
| **Exercise execution** | No code execution | Compiles + runs Rust code, compares output |
| **Agent architecture** | Skills on single agent | Multi-agent crew with coordinator |
| **Question traceability** | Questions exist but no formal provenance chain | Every question traces to source quote + objective |
| **Cognitive load management** | Best practices taught inline | Best practices deferred to review phase |
| **Progress tracking** | JSONL-based SR per topic | SQLite-based SM-2 per topic AND per card |
| **Flashcard format** | JSONL questions reused as cards | Dedicated card files with stable IDs, Anki export |
| **Curriculum navigation** | MAP.md with DAG visualization | Python scripts + predefined learning paths |
| **First-time experience** | Ask what to learn, scaffold workspace | Ask background, select path, start immediately |

## Architecture Notes

- **Web stack**: Rust (Axum) + Tera templates + Tailwind CSS + HTMX-style partials
- **Database**: SQLite with migrations (topic_progress, card_progress, telemetry, sandbox)
- **SM-2 implementation**: Both Python scripts (CLI) and Rust module (web) implement the same algorithm
- **Code execution**: `rustc --edition 2021` compile + 5s timeout, sandboxed in scratch/
- **Agent config**: JSON agent definitions with tools, resources, hooks, and keyboard shortcuts
- **Crew orchestration**: YAML crew file (24KB) defining the full pipeline

## Open Questions

- How does the web app handle multi-user? (Appears single-user: one SQLite DB, no auth)
- What happens when Rust by Example updates? (Documented: regenerate, don't patch)
- Is there a formal prerequisite graph beyond chapter ordering? (Partial: chapters declare prerequisites/unlocks, but no DAG visualization)
