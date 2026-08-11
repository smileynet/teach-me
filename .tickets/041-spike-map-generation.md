---
id: "041"
title: "Spike: MAP.md generation quality — can the agent decompose domains well?"
status: done
priority: high
blocked_by: []
type: spike
---

# Spike: MAP.md generation quality

## Question to answer

Given a broad topic, can the teach skill reliably produce a well-structured MAP.md with 5-9 subtopics, reasonable soft prerequisites, and useful leads_to?

## Why spike first

The quality of generated maps determines if the whole domain scaffolding feature is useful or confusing. Bad topic decomposition = bad learning experience. This is the make-or-break question.

## Method

1. Define the MAP.md format (from proposal)
2. Test generation with 3-5 diverse domains:
   - "modern data analytics stacks" (the motivating example)
   - "game development with Godot"
   - "distributed systems fundamentals"
   - "web application security"
3. For each: research → generate MAP.md → evaluate

## Evaluation criteria

- Are there 5-9 subtopics? (not 3, not 15)
- Is the granularity right? (each subtopic = 2-4 lessons, not 1 and not 10)
- Are prerequisites sensible? (soft, directional, no cycles)
- Are leads_to domains real and useful?
- Would a newcomer understand the "why" for each subtopic?
- Is anything obviously missing?

## Success criteria

- [ ] MAP.md format defined and documented
- [ ] 3+ domains tested
- [ ] 3/3 generated maps are usable without major restructuring
- [ ] Failure modes identified (if any)

## Expected output

Generated MAP.md files in `.scratch/` + evaluation notes. If successful, proceed to ticket 042 (parser) and 043 (orientation lesson).

## Findings (2026-08-11)

**Result: Works. 3/3 maps usable without edits.**

### Quality evaluation

| Domain | Topics | DAG | Scope | leads_to | Verdict |
|--------|--------|-----|-------|----------|---------|
| Data analytics | 7 | clean chain | 1 deep, 6 substantial | 5 real domains | ✓ usable |
| Godot gamedev | 8 | natural branches | 2 deep, 5 substantial, 1 lightweight | 5 real domains | ✓ usable |
| Web security | 9 (ceiling) | multiple entry points | 7 substantial, 2 lightweight | 4 real domains | ✓ usable |

### What worked

1. Format spec produces consistent output — all 3 maps follow the structure exactly
2. 5-9 constraint naturally produces the right granularity
3. "Why" framing forces connection to learner goals (not just "what" descriptions)
4. Scope markers (lightweight/substantial/deep) signal where sub-MAPs might be warranted
5. Per-topic leads_to emerged naturally for the Godot map (nodes→AI, animation→shaders)

### Minor issues (not blockers)

1. At 9 topics (web security), the map feels dense. 6-7 is the sweet spot.
2. Some judgment calls on topic boundaries are debatable (physics as separate vs part of 2D) — but this is true of any curriculum design. The important thing is it's defensible.
3. leads_to quality depends on the agent knowing adjacent domains. All 3 produced real, useful supertopic suggestions.

### Failure modes NOT observed

- Over-decomposition (>9 topics): didn't happen — the 5-9 constraint was respected
- Under-decomposition (<5): didn't happen — all domains had enough natural structure
- Cycles in prereqs: none detected
- Unreasonable prereqs: none — all follow logical dependency

### Decision

Proceed to ticket 043 (MAP.md parser). The format is validated and generation quality is sufficient for production use.

### Generated files

- `.scratch/spike-041/data-analytics.MAP.md`
- `.scratch/spike-041/godot-gamedev.MAP.md`
- `.scratch/spike-041/web-security.MAP.md`
