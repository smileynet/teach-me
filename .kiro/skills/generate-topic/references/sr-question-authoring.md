# SR Question Authoring

The single source of truth for how to write spaced-repetition questions in teach-me.
generate-topic Phase 2 step 4, quiz-me, and the teach skill all defer here — do not
restate these rules elsewhere.

**Contents:** Archetypes · Criteria format · Another Angle (eli5) · Provenance & level
tagging · Interactive question types · Difficulty progression.

Per topic: **4–8 open-answer questions + 2–3 interactive questions.**

## Open-Answer Question Archetypes (use at least 3 different types per topic)

| Archetype | Framing | Tests | When to use |
|-----------|---------|-------|-------------|
| **Explain-why** | "Why does X work this way?" / "Why not Y instead?" | Causal understanding | Core mechanism of the lesson |
| **Scenario** | "You're building X and encounter Y. What do you do?" | Application under constraints | Practical skills, decision-making |
| **Predict** | "If you change X, what happens to Y?" | Mental model accuracy | Config, parameters, dependencies |
| **Debug** | "This isn't working: [symptom]. What went wrong?" | Diagnostic reasoning | Common mistakes from the lesson |
| **Teach-back** | "Explain to [specific person] how to..." | Deep synthesis | Integration across concepts |
| **Connect** | "How does X relate to [concept from earlier lesson]?" | Transfer across topics | Cross-topic relationships |

**Do NOT** make all questions the same archetype. Variety of surface form forces genuine understanding vs pattern-matching the lesson text.

## Criteria Format (REQUIRED — enforced by `sr:check`)

Every open-answer question MUST have a `criteria` field with this structure:

```
"criteria": "Should mention: (1) first key point, (2) second key point, (3) third key point. Bonus: stretch insight that shows deep understanding."
```

Rules:
- 2-4 numbered must-mention points — specific and testable
- 1 bonus point — the "aha" insight that proves deep understanding
- Each point is a *concept to address*, not exact wording to reproduce
- Key insight: identify the ONE sentence that distinguishes understanding from memorization

## Another Angle (REQUIRED for new questions)

Every open-answer question MUST include an `eli5` field:

```json
{"prompt": "...", "criteria": "...", "eli5": "Think of it like..."}
```

The `eli5` is NOT a simpler version — it's a *different angle*: an analogy, concrete example, or reframing that helps the concept click from a second direction. Shown to the user as "Another angle" alongside the criteria.

## Provenance & Level Tagging (REQUIRED for new questions — ADR 0007)

**If `.scratch/concepts/{slug}.json` exists**, read it before writing questions:
- Use concept `level` field for the `tags` L-level (L1/L2/L3)
- Prioritize questions on concepts with highest `score` (most foundational)
- Use `edges[].suggestion` for relationship-type questions ("explain why X depends on Y")
- Ensure at least one question per concept above `coverage_target`

If no concept hints file exists, assign L-levels by judgment (as before).

Every open-answer question SHOULD include these fields:

```json
{
  "prompt": "...",
  "criteria": "...",
  "eli5": "...",
  "source_section": "The heading of the lesson section this question tests",
  "source_page": 14,
  "source_quote": "The exact sentence or passage from the lesson that teaches this answer",
  "derivation": "direct",
  "tags": ["L1-core"]
}
```

**`source_section`** — The heading (H2/H3) of the lesson section this card was derived from. Shown in the quiz UI after answering as "📖 From: §source_section".

**`source_page`** — The page number or chunk index from the source document. Shown alongside source_section when available.

**`source_quote`** — The passage from the lesson that teaches what this question tests. Enables re-read routing when the learner fails a card. REQUIRED for `derivation: "direct"` questions; optional for inference/synthesis.

**`derivation`** — How the answer relates to lesson content:
- `"direct"` — answer found in a single passage (cite it in source_quote)
- `"inference"` — requires connecting ideas within the lesson
- `"synthesis"` — spans multiple sections or cross-topic

**`tags`** (level tagging) — cognitive load tier:
- `["L1-core"]` — fundamental concepts, always true, tested first
- `["L2-practice"]` — best practices, usually-true rules, tested after core consolidates
- `["L3-nuance"]` — edge cases, "it depends", mastery-level

Order in JSONL: L1 questions first, then L2, then L3. This is the implicit difficulty progression.

## Interactive Questions (2-3 per topic)

Include a mix of:
- `"type": "sequence"` — ordering steps/hierarchy (with `items` + `correct_order`)
- `"type": "match"` — connecting terms to definitions (with `pairs`)
- `"type": "fill"` — completing key statements (with `template` + `answers`)

These test recognition and recall; open-answer questions test deeper understanding. Both are needed.

## Difficulty Progression (implicit, never labeled)

Order questions in the JSONL from recognition → application → synthesis. Don't label difficulty — users feel the progression naturally. First questions should be approachable (explain-why about the core concept); later questions should require combining ideas (connect, predict, debug).
