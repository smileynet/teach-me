# ADR 0007: Adopt research patterns for lesson and question quality

## Status

Accepted (2026-08-17)

## Context

Research ticket #135 identified 5 patterns from prior art (Rustacean Academy, coding-best-practices) and academic literature. Ticket #136 evaluated each for applicability to teach-me's existing web-researched pipeline.

## Decisions

### Pattern 1: Provenance chain → ADOPT-LIGHT

**What:** Add `source_quote` field to new questions (the passage that teaches the answer).

**Why:** Enables stale-question detection, re-read routing on failed SR cards, and the "Could They Answer This?" quality check. Existing questions already have `topic` + `source` URL — adding the actual quote closes the provenance gap.

**Convention:** New questions SHOULD include `"source_quote": "exact text from lesson that teaches this"`. Optional for synthesis questions that span multiple sections.

### Pattern 2: Cognitive load separation → ADOPT-LIGHT (tagging only)

**What:** Tag SR questions with `L1-core` / `L2-practice` / `L3-nuance` in existing `tags` field.

**Why:** Enables future proficiency-gated scheduling without requiring code changes now. At current scale (4-15 cards/topic), manual tag helps the agent sequence questions during generation.

**Convention:**
- L1-core: fundamental concepts, always true, tested first
- L2-practice: best practices, usually-true rules, introduced after L1 consolidates
- L3-nuance: edge cases, exceptions, "it depends" answers, mastery-level

No scheduler gating now. Revisit when any topic exceeds 20 cards.

### Pattern 3: Conflict surfacing → ADOPT-LIGHT (CSS class + convention)

**What:** Define a `[!conflict]` callout style. Document the convention that disagreements surface in reference docs, not lessons.

**Why:** Prepares the ground for multi-source enrichment (#141). Zero implementation cost — just CSS and guidance.

**Convention:** When sources disagree, the reference doc includes:
```html
<div class="conflict-callout">
  <strong>Sources disagree:</strong> A says X, B says Y.
  In practice, [resolution or "depends on context"].
</div>
```

Lessons present one coherent path. Conflicts appear only in reference docs and L3 SR cards.

### Pattern 4: Situation index → DEFER (prepare conventions only)

**What:** Not building the situation index page yet. But formalize that every lesson MUST have a "The Problem" section with extractable symptoms.

**Why:** Value comes at 10+ topics per workspace. Current map navigation suffices at 2-7 topics. The convention ensures future lessons are pre-adapted for extraction.

**Convention:** Every lesson starts with `<h2>The Problem: [tension]</h2>` containing bullet symptoms. This is already the scaffold pattern — just enforce it.

### Pattern 5: "Could They Answer This?" gate → ADOPT-RELAXED

**What:** Add `derivation` field to questions: `direct` (answer in one passage), `inference` (requires connecting ideas), `synthesis` (cross-section/cross-topic).

**Why:** The strict gate (every question traces to one passage) would kill teach-me's best questions — the explain-to-a-colleague application questions that require inference. The relaxed version preserves these while still catching hallucinated questions.

**Convention:**
- `derivation: "direct"` — passage cited in source_quote directly answers this
- `derivation: "inference"` — answer requires combining ideas from the lesson
- `derivation: "synthesis"` — spans multiple sections or topics

`sr:check` flags questions with derivation=direct but no source_quote.

## Implementation

All adopted patterns are convention/guidance changes (update SKILL.md) with optional sr:check validation. No architectural changes. No migration of existing questions.

| Pattern | Change type | Effort | Files affected |
|---------|-------------|--------|---------------|
| Provenance (source_quote) | Skill guidance | 10 min | generate-topic SKILL.md |
| L1/L2/L3 tags | Skill guidance | 10 min | generate-topic SKILL.md |
| Conflict callout | CSS + guidance | 15 min | style.css, teach skill |
| Situation convention | Already exists | 0 min | — (enforce in review) |
| Derivation field | Skill guidance + sr:check | 20 min | generate-topic SKILL.md, sr-check.py |

## Consequences

- New questions will carry richer metadata with zero migration cost
- Future features (re-read routing, proficiency gating, situation index) are pre-adapted
- No breaking changes to existing content
- sr:check becomes slightly more opinionated (flags missing source_quote on direct questions)
