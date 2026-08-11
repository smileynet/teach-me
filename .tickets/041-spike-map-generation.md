---
id: "041"
title: "Spike: MAP.md generation quality — can the agent decompose domains well?"
status: open
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
