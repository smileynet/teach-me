---
id: "020"
title: "Spike: problem-first lesson opening"
status: done
priority: high
blocked_by: []
type: spike
---

# Spike: problem-first lesson opening

## Hypothesis

Starting lessons with "what's broken/missing" before presenting the solution improves engagement and comprehension. GDQuest does this consistently with measurable structural patterns (gap demonstration, broken-state preview, scaffolded limitations).

## What to build

Rewrite lesson 1's opening to follow the problem-first pattern:
1. Open with the pain (what breaks at scale with traditional data lakes)
2. Make it concrete (one specific failure mode the learner can visualize)
3. THEN introduce Iceberg as the solution

Also update the teach skill with the "Problem Opening" requirement.

## Baseline

Current lesson 1 opening: jumps to "A traditional data lake is just files in S3 with a schema bolted on top" — this IS problem-first to some degree, but doesn't make the learner *feel* the gap before naming the solution.

## Compare against

- Does the new opening create a stronger "why should I care?" moment?
- Is it still concise (not bloated)?
- Does it flow naturally into the existing content?

## Acceptance criteria

- [ ] Lesson 1 opening rewritten with explicit problem-first structure
- [ ] Teach skill documents the pattern with examples
- [ ] Side-by-side comparison presented for review (before/after)
