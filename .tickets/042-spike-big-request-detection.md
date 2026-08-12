---
id: "042"
title: "Spike: big-request detection — domain mode vs focused topic"
status: open
priority: low
blocked_by: []
type: spike
---

# Spike: big-request detection

## Question to answer

Can the teach skill reliably distinguish "teach me about modern data stacks" (domain → MAP.md) from "teach me about Iceberg partition pruning" (focused → single lesson)?

## Why this matters

False positives (generating a MAP.md for a focused request) waste time and frustrate the learner. False negatives (treating a broad request as focused) produce superficial lessons that don't help.

## Method

1. Collect 15-20 example requests spanning the spectrum:
   - Clearly broad: "data engineering", "cloud architecture", "game dev"
   - Clearly focused: "Iceberg manifest files", "Spark shuffle optimization", "ECS vs inheritance"
   - Borderline: "Kubernetes", "React", "machine learning"
2. For each: what should the skill do? (MAP.md / single topic / ask to clarify)
3. Test the detection heuristic against all examples
4. Measure: false positive rate, false negative rate

## Proposed heuristic

```
IF topic would require 4+ lessons to cover adequately
AND learner hasn't scoped it down ("just the basics", "specifically X")
THEN → domain mode (generate MAP.md)

IF borderline
THEN → ask: "[Topic] is broad. Want the full landscape, or focused on [detected subtopic]?"
```

## Success criteria

- [ ] < 10% false positives (broad treatment of focused requests)
- [ ] < 20% false negatives (focused treatment of broad requests)
- [ ] Borderline cases get a clarifying question (not a wrong guess)

## Expected output

Decision table mapping requests → actions. Heuristic ready to embed in teach skill.
