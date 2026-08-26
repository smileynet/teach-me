---
id: "031"
title: "Feature: soft-recommend review before new lessons"
status: done
priority: medium
blocked_by: []
type: feature
tags: [platform]
---

# Feature: soft-recommend review before new lessons

## Current state

The teach skill already has guidance to run `sr-status.py` at session start and surface due cards before new material (Socratic Gate section). The `sr-status.py` script exists and works. What remains is **verifying the behavior works end-to-end in a real teaching session** and potentially adding a helper that formats the recommendation message consistently.

## What to build

When SR cards are due, the teach skill mentions it and recommends reviewing — but always provides new content if asked. Never block, never force an override. The posture is "provide if asked" — the learner is in charge of their schedule.

## Design

At session start or before a new lesson, if cards are due:

```
📚 You have 4 cards due for review (iceberg-on-aws).
   A quick review helps cement what you've already learned.
   Want to do a few review questions first, or jump straight to new material?
```

If they say "new material" — give them new material, no friction. If they say "review" — surface due cards conversationally.

## Principles

- **Recommend, never gate.** The learner knows their schedule and energy.
- **Provide if asked.** If they want new content, deliver it immediately.
- **Mention, don't nag.** One line at session start. Don't repeat mid-lesson.
- **Data-informed recommendation.** If retrievability is dropping fast (below 70%), make the recommendation stronger but still not blocking: "Several concepts from last lesson are decaying — reviewing now would strengthen them."

## What NOT to do

- Don't require the learner to say "skip" or "override" — that's a gate with a different name
- Don't explain SM-2 or retrievability math to the learner
- Don't repeat the recommendation after they've chosen to continue
- Don't frame it as a test they need to pass

## Acceptance criteria

- [x] teach skill checks sr-status at session start
- [x] If cards due: one-line recommendation, ask preference
- [x] If learner asks for new content: provide it without friction
- [x] Recommendation strength scales with decay (mild at 85% R, firmer at <70%)
- [x] Never uses language like "you must", "required", "before you can"

## Resolution (closed 2026-08-10)

Shelved. A session-start review nudge adds friction to a casual exploration tool. The user opens a session because they're curious about something new — a "you have cards due" prompt is noise they'll dismiss every time. SR review is pull-based (`mise run sr`, `mise run sr:review`) and the learner reaches for it when the mood strikes. The teach skill guidance already mentions due cards if asked "what should I do?" — that's sufficient without formalizing a recommendation flow.
