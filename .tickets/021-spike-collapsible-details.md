---
id: "021"
title: "Spike: collapsible details pattern (deep dives, reminders, hints)"
status: done
priority: high
blocked_by: []
type: spike
tags: [platform]
---

# Spike: collapsible details pattern

## Hypothesis

`<details>` elements enable three GDQuest techniques simultaneously: optional deep dives (don't interrupt flow), prior-knowledge reminders (just-in-time refresh without re-explaining), and progressive challenge hints. Adding CSS styling + documenting the pattern unlocks all three.

## What to build

1. Add `<details>` styling to `assets/style.css` (~5 lines)
2. Add 2-3 examples to lesson 1:
   - One deep dive ("Why Avro for manifests and not JSON?")
   - One reminder in a later section ("Reminder: how the catalog pointer works")
3. Document the three use cases in the teach skill

## Baseline

Current lesson 1 has no collapsible content. All information is inline at the same hierarchy level — the learner must read everything linearly.

## Compare against

- Does it reduce perceived lesson length?
- Do the deep dives feel optional (not required for comprehension)?
- Do reminders feel helpful vs patronizing?

## Acceptance criteria

- [x] `<details>` CSS added to style.css
- [x] 2-3 examples added to lesson 1
- [x] Teach skill documents when to use each variant
- [x] Before/after comparison presented
