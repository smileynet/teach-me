---
id: "322"
title: "Review: adopt happy-path-first spiral as universal teaching structure, or one style among several"
status: open
blocked_by: ["305"]
validation_criteria:
  - "Applied the DRAFT guidance to the 7 godot-asset-pipeline topic tickets and evaluated the result against the universality test"
  - "Decision recorded (adopt-universally vs document-as-one-style) with the test outcome for each shipped domain"
  - "Guidance landed in visual-teaching.md (adopted or as one style among documented alternatives); alternative styles documented"
tags: ["content"]
---

# Review: adopt happy-path-first spiral as universal teaching structure, or one style among several

## Context

While scoping #305 (godot-asset-pipeline topics) the user directed a specific teaching structure:
**start with the happy path (an early win), then spiral outward to broader sub-cases — each
sub-topic is its own win → complication → resolution → win loop, and the track leads with a pure
happy-path topic (topic 0).** This was drafted as guidance and executed once (the 7
godot-asset-pipeline topic tickets) but deliberately NOT yet adopted into steering.

Draft guidance: `.scratch/proposals/track-topic-structure-guidance-DRAFT.md`
Executed instance: `.scratch/proposals/305-godot-asset-pipeline-setup.md` (§ topic table, 7 topics 0–6).

## What to build

Evaluate whether the drafted "happy-path-first spiral" structure should be adopted **universally**
(a — into `visual-teaching.md` as THE topic/track structure) or **selectively** (b — documented as
one style among several, with explicit criteria for when each applies). Consider and DOCUMENT
alternative styles, not just this one.

**The decisive test:** *"Would this structure make ALL existing topic/domain lessons stronger?"*
Apply it concretely against each shipped domain — gltf-format, godot-gamedev, iceberg-workspace,
oidc-rust, workout-fundamentals, ink-godot. If yes across the board → adopt universally. If some
domains are stronger in a different shape (e.g. gltf-format's anatomy-first / first-principles
order may be intentional) → the structure is one style among several; document when to pick which.

Alternative styles to weigh (from the draft; extend as needed):
- **Happy-path-first spiral** (this proposal) — early win, then widen; each topic win→complication→win.
- **Depth-first / first-principles** — build the mental model bottom-up before any end-to-end run.
- **Problem-first / case-driven** — open with the learner's existing failure, diagnose outward.
- **Reference / breadth-first** — survey the space, then drill (lookup-oriented tracks).

Dispatch a review subagent per shipped domain (read its MAP + a lesson or two) to judge fit against
the test — don't evaluate from memory. Then synthesize the adopt-vs-selective decision.

## Acceptance criteria

- [ ] Draft guidance applied to the 7 godot-asset-pipeline topic tickets (done at #305 scope time) and the result assessed against the universality test
- [ ] Each shipped domain evaluated against "would this make its lessons stronger?" — outcome recorded per domain (subagent-reviewed, not from memory)
- [ ] Decision recorded: adopt-universally (a) vs one-style-among-several (b), with rationale
- [ ] `visual-teaching.md` updated — either the structure adopted as the default, or the structure + its alternatives documented with when-to-use-which criteria
- [ ] If a durable decision with a rejected alternative results → ADR in `.memory/adr/`
- [ ] teach/SKILL.md gets the companion checklist pointer IF adopted as default

## Notes

- Blocked by #305 (this structure is being trialed on that domain's topics first).
- Do NOT bulk-rewrite existing lessons as part of this ticket — this decides + documents the
  convention; any re-authoring is separate, opt-in follow-up work.
