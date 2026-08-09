---
id: "029"
title: "Feature: Socratic gate dialog before progression"
status: open
priority: high
blocked_by: []
type: feature
---

# Feature: Socratic gate dialog before progression

## Context

Currently, the learner can say "next lesson" and the agent proceeds without any check. Reading ≠ understanding. Pocock's documentation identifies this as a core design choice: "a quiz is a gate, not a formality." Multiple users of his skill report that the agent pushes back if they try to move on without demonstrating understanding.

Our learner's JTBD: they need to advise teams and architect systems. The real test of understanding isn't "can you name the layers?" — it's "can you explain to a skeptical engineer why this design matters?" The gate should simulate that conversation.

## Intent

The Socratic gate is the agentic interaction that turns passive reading into active understanding. It's the core differentiator between "consume an artifact" and "learn with a teacher." The agent acts as a rehearsal partner for the conversations the learner will have at work.

This is NOT:
- A quiz (multiple choice, one correct answer)
- An exam (pass/fail, scored)
- A blocker (learner can opt out)

This IS:
- A brief conversational exchange where the learner explains and the agent probes
- A rehearsal of real work conversations from the learner's mission
- A mechanism that produces learning records (what was demonstrated vs not)
- The transition from "I read it" to "I can explain it"

## What to build

### 1. Gate behavior in teach skill

After a lesson is delivered and the learner has read it, the agent asks ONE probing question before progressing. The question is framed as a scenario from their mission.

### 2. Question design guidance

```
Frame: "[Person from your mission context] asks: [real question they'd ask]."
       "Walk me through your answer."

Good examples:
- "A data producer asks: why can't we just partition by date and let Glue 
  crawl it? What do you tell them?"
- "Your architect asks: what guarantees do we get if two Spark jobs write 
  simultaneously? Explain."
- "A stakeholder asks: can we change the partitioning scheme after launch 
  without downtime? Walk me through it."

Bad examples:
- "What are the five layers?" (recall)
- "Define MVCC." (textbook)
- "What did you learn?" (too open, no structure)
```

### 3. Dialog rules

- **2-3 exchanges max.** Ask → learner responds → ONE follow-up if needed → done.
- **The learner explains, the agent probes.** Agent never re-teaches during the gate. It asks "what enables that?" or "what would break if we didn't have that?"
- **Follow-ups go deeper, not wider.** Drill into the answer given, don't pivot to a new topic.
- **If stuck after 2 attempts:** "Let's revisit the [X] section — the key thing to focus on is [Y]." Then offer the lesson section, don't re-explain from scratch.
- **Graceful exit:** Learner says "I want to move on" → agent accepts, records what wasn't demonstrated, moves on. No guilt, no blocking.

### 4. Learning record from the gate

After the exchange, write a learning record capturing:
- What was demonstrated (which concepts the learner explained correctly)
- What wasn't demonstrated (gaps, partial understanding, skipped)
- This directly feeds ZPD calculation for the next lesson

### 5. Example dialog (include in skill)

```
Agent: "Before we move on — imagine your customer's data architect asks: 
       'Why do we need Iceberg? We already have Glue crawlers discovering 
       our partitions.' What's your answer?"

Learner: "Because crawlers still have to list S3, which is slow at scale, 
         and there's no consistency guarantee during the crawl."

Agent: "Good — you've got the listing problem and the isolation gap. 
       What specifically does Iceberg use instead of listing to find files?"

Learner: "The manifest files track exactly which data files exist, with 
         stats per file, so the engine never lists S3."

Agent: "That's the core insight. Ready for the next topic, or want to 
       dig into any part of this more?"
```

## Validation

- [ ] The gate question references people/scenarios from MISSION.md (not generic)
- [ ] The learner demonstrates understanding in their own words (not parroting the lesson)
- [ ] The exchange is ≤3 turns total (not an interrogation)
- [ ] A learning record is produced after the exchange
- [ ] If the learner opts out, it's recorded without penalty

## Acceptance criteria

- [ ] Teach skill documents gate dialog as part of the lesson→next-lesson flow
- [ ] Gate question framing guidance with good/bad examples
- [ ] Dialog rules (2-3 max, probes deeper not wider, graceful exit)
- [ ] Learning record format for gate outcomes
- [ ] Example dialog showing the full exchange
- [ ] The gate is conversational (Socratic), not evaluative (quiz)
