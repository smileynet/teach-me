---
id: "089"
title: "Feature: deepen Socratic dialog — full context for accurate discussion"
status: open
blocked_by: []
priority: medium
tags: [platform]
---

# Feature: deepen Socratic dialog — full context for accurate discussion

## Problem

When a user asks for a Socratic dialog ("quiz me", "test my understanding"), the agent needs full context about:
1. What the lesson actually taught (specific claims, diagrams, examples)
2. What sources were used (to verify the learner's statements against facts)
3. What the learner has previously demonstrated understanding of (learning records)
4. What adjacent topics connect (to probe deeper or redirect)

Currently the quiz-me skill operates with whatever's in the conversation context — which may be stale or incomplete if the user is returning after reading HTML lessons in their browser.

## What to build

1. **Context loading**: When Socratic dialog is triggered, the agent should read:
   - The lesson HTML for the topic being discussed
   - The reference doc (key facts in lookup form)
   - The SR questions + expected answers (criteria for "correct")
   - The learner's MISSION.md (to ground questions in their goals)
   - RESOURCES.md (to cite sources when correcting misconceptions)

2. **Accuracy grounding**: The agent's responses during dialog should be grounded in the lesson content and cited sources — not parametric memory. If the learner states something that contradicts a lesson claim, the agent cites the specific source.

3. **Depth probing**: After the learner explains a concept correctly, the agent should:
   - Ask about edge cases or limitations mentioned in the lesson
   - Ask how this connects to prerequisites or upcoming topics
   - Ask the learner to apply the concept to their mission context

4. **Progress tracking**: Record demonstrated understanding from the dialog as a learning record (not just SR card ratings).

## Acceptance criteria

- [ ] quiz-me skill reads the relevant lesson + reference before starting dialog
- [ ] Agent corrections cite specific sources from RESOURCES.md
- [ ] Dialog probes connections to adjacent topics in the MAP
- [ ] Demonstrated understanding recorded (learning-records/)
- [ ] Agent never contradicts lesson content during dialog
