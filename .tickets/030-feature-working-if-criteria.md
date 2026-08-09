---
id: "030"
title: "Feature: 'it's working if' system performance criteria"
status: open
priority: high
blocked_by: ["028", "029"]
type: feature
---

# Feature: "it's working if" system performance criteria

## What this is

Observable indicators that the teach-me system is performing well. Not evaluating the learner (the gate dialog does that) — evaluating whether the *system* is doing its job as a teaching tool.

This is Pocock's pattern: success criteria for the skill itself. "You know this system is working if you observe these things. You know it's broken if you observe those things."

## Proposed criteria

### It's working if:

- The first thing it does in an empty workspace is interview about mission, not produce a lesson
- RESOURCES.md populates before lessons — it researches, then teaches from what it found
- Claims in lessons carry citations. A lesson with no links is teaching from memory.
- A lesson takes one sitting and leaves the learner able to explain one thing they couldn't before
- The gate dialog feels like rehearsing a real work conversation, not taking an exam
- Learning records grow, and later lessons build on demonstrated understanding rather than re-teaching
- Reference docs are useful standalone — someone who never read the lesson can use one at their desk
- Opening a fresh session in the workspace and saying "next lesson" continues where it left off
- The glossary annotates terms the learner wouldn't know, and doesn't annotate obvious ones
- A question that needs real-world judgment gets a resource pointer, not just an answer

### It's NOT working if:

- It produces a lesson before understanding why the learner cares
- Lessons cite no sources — the agent is teaching from parametric memory
- The learner can say "next lesson" without any conversational check
- Reference docs are just shorter lessons (narrative) not scannable artifacts
- The gate asks "what is X?" instead of "explain to [person from your mission] why..."
- Every lesson re-explains concepts from lesson 1 regardless of learning records
- The workspace accumulates files but the learner reports no improvement in their work conversations

## Acceptance criteria

- [ ] "It's working if" section added to teach skill
- [ ] Criteria evaluate the system, not the learner
- [ ] Criteria are observable from workspace state + dialog patterns
- [ ] "It's NOT working if" anti-patterns documented
