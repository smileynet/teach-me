---
id: "029"
title: "Feature: Socratic gate dialog before progression"
status: open
priority: high
blocked_by: []
type: feature
---

# Feature: Socratic gate dialog before progression

## What to build

After the learner reads a lesson, the agent initiates a short Socratic exchange to verify understanding before moving to the next topic. The learner explains; the agent probes. This simulates the real conversations they'll have at work.

## Design

### The flow

```
Lesson delivered → Learner reads → Agent asks a probing question →
Learner explains in their own words → Agent follows up (if needed) →
Understanding confirmed → Learning record written → Ready for next
```

### Probing questions match the mission

The gate question should simulate a real-world conversation from the learner's mission:

- Good: "If a data producer asks you why they can't just partition by date and let Glue crawl it, what would you tell them?"
- Good: "A stakeholder asks: 'what happens if two teams write at the same time?' Walk me through it."
- Bad: "Name the five layers of the metadata tree." (recall, not application)
- Bad: "What is MVCC?" (definition, not understanding)

The question should be answerable by someone who understood the lesson's core insight, framed as a conversation they'll actually have.

### Dialog rules

- **2-3 exchanges max** — not an interrogation
- **The learner explains, the agent probes** — agent doesn't re-teach during the gate
- **Follow-ups go deeper, not wider** — "Right, but what specifically enables that?" not "Also, what about X?"
- **If stuck after 2 attempts** — agent says "Let's revisit [specific section]" and points back
- **Graceful exit** — learner can say "I want to move on" and the agent accepts. But it records what wasn't demonstrated.
- **Learning record captures the outcome** — what was demonstrated, what wasn't. Drives ZPD for next lesson.

### Not a separate skill

This is behavior added to the teach skill's flow, not a standalone skill invocation. When the learner says "next lesson" or the teach skill finishes writing one, the gate activates before progression.

## Acceptance criteria

- [ ] Teach skill documents the gate dialog pattern
- [ ] Gate questions framed as mission-relevant conversations (not recall)
- [ ] 2-3 exchange limit documented
- [ ] Learning record captures demonstration outcome
- [ ] Graceful exit option documented
- [ ] Example dialog in the skill showing good probing
