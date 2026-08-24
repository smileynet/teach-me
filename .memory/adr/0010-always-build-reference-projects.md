# ADR 0010: Always Build Reference Projects Alongside Lessons

**Status:** Accepted  
**Date:** 2026-08-24  
**Context:** Ticket #193 (design decision 5), validated by MKToon track experience

## Decision

Every lesson track that produces code MUST build a live reference project alongside the lessons. Learners should be able to run the artifact, not just read about it.

## Context

The MKToon shader track (0009–0014) validated this approach empirically:
- Each lesson produces a `.gdshader` file that compiles and runs in `test-scene/`
- The final shader (190 lines) is the culmination of 6 lessons — a real artifact, not just documentation
- Validation was possible because the artifact existed (Godot headless import)
- The "shipped game reference" (mk_toon_lite.gdshader) sits alongside learner-built versions for comparison

Without a reference project:
- Code blocks go untested until a learner reports breakage
- "Does this actually work?" has no answer without manual checking
- Learners can't experiment beyond what the lesson shows
- The lesson is documentation pretending to be a tutorial

## The Practice

### For every new lesson track:

1. **Scaffold a reference project** at the track setup stage (like `test-scene/` for shaders)
2. **Each lesson produces a runnable artifact** — a file that goes into the project
3. **The final lesson's artifact is the complete product** — everything prior builds toward it
4. **Validate via the project's toolchain** — compile, import, lint, run (headless if possible)
5. **Include a "shipped game" comparison** when available — a reference artifact that shows how a real product solved the same problem

### What counts as a "reference project":

| Track type | Reference project | Validation method |
|------------|-------------------|-------------------|
| Shader lessons | Godot test-scene with meshes + materials | `godot --headless --import --quit` |
| Ink/narrative | Godot project with ink stories + UI scenes | Story compiles via inklecate + scene loads |
| Web/API | Running server or app | `curl` / Playwright |
| Data/pipeline | Processing scripts + sample data | Script runs, output matches expected |
| Pure language | REPL-testable files | Language compiler/interpreter check |

### What does NOT count:

- Code blocks in HTML with no corresponding file on disk
- "This is what the code would look like" without a runnable version
- A reference project created after the fact (must grow alongside lessons)

## Consequences

1. Track setup tickets (like #186) ALWAYS include "create reference project" as an acceptance criterion
2. Lesson generation validates against the project before closing
3. The `reference/code/{lesson-slug}/` pattern continues (downloadable per-lesson artifacts)
4. New tracks must identify their validation toolchain BEFORE generating lessons
5. `mise run verify` eventually covers all reference projects (not just shaders)

## Related

- ADR 0009 (MKToon sibling fork) — established the test-scene pattern
- `.kiro/steering/code-validation-teaching.md` — the validation contract for code-based lessons
- Ticket #193 — first application beyond shaders (ink stories as artifacts)
