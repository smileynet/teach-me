# 0019 — teach and generate-topic ownership boundary

**Status:** accepted
**Date:** 2026-10-21

## Context

The skill-effectiveness review (#346) found that `teach` and `generate-topic` each presented
overlapping pipeline authority. Both documents described a full authoring procedure
(research → lesson → reference → SR → quiz → verify): `teach` as steps 4–7 of its workflow,
`generate-topic` as its Phase 2. The boundary existed only as one soft sentence at the bottom
of each skill ("teach is the creative engine; this is the assembly line"). Because the two
procedures were near-duplicates that could drift independently, equivalent requests ("teach me
X" vs "generate a lesson on X") could route to either skill and pick up contradictory
instructions, risking duplicate generation or untracked learner-state writes. Ticket #360
required a distinct, complementary ownership with explicit handoff.

## Decision

Keep both skills — consolidation was rejected by #346 and the two have genuinely different
invocation modes (`teach` is user-only, conversational, stateful; `generate-topic` runs as a
batch pipeline invoked by `teach`, a user, or map-driven generation). Draw the boundary by
outcome, not by lexical trigger:

- **`teach` owns the conversational learning engine**: first-contact orientation, mission
  elicitation, ZPD selection (what to teach next), re-explanation of existing material,
  Socratic follow-ups, zoom/map navigation, and all learner-state writes (under `.user/`). It
  may produce an explicit, untracked throwaway draft in a live session.
- **`generate-topic` owns the durable authoring assembly line** and is the **single source of
  truth for the authoring sequence** (its Phase 1–4). It owns completeness, the verify gate,
  and the committed graph-data writes on success.
- When `teach` needs a tracked, verified artifact it **invokes** `generate-topic` rather than
  re-running the steps. `teach` picks the node; `generate-topic` authors it.

Each skill now carries a mirrored "Ownership & Routing" section (owned outcomes, non-goals,
handoff triggers). A single routing table (in `teach`, cross-referenced from `generate-topic`)
maps representative prompts to exactly one owner. The resolving rule when two could match:
**durable + verified artifact → `generate-topic`; conversation, orientation, or
re-explanation → `teach`.** SR-question structure remains singly owned by
`generate-topic/references/sr-question-authoring.md` (pre-existing); `teach`'s publish
checklist is reframed as its acceptance contract — the qualities `generate-topic` must honor —
not a second procedure.

## Consequences

- Equivalent requests route to one named owner without contradictory instructions (the #360
  validation criterion). Readers and agents resolve "teach me / generate a lesson / complete a
  topic" deterministically via the routing table.
- The authoring sequence has one place to change. Edits to how lessons are produced happen in
  `generate-topic` Phase 2; `teach` links to it instead of mirroring it, so the two can no
  longer drift.
- The knowledgeable-colleague posture (ADR 0001) and the research-before-authoring hard gate
  are preserved: posture and pedagogy live in `teach` + `visual-teaching.md`, which
  `generate-topic` applies but does not redefine.
- Cost: `teach` can no longer be read end-to-end as a self-contained authoring recipe — the
  durable path now requires following the handoff into `generate-topic`. The explicit
  throwaway-draft exception keeps the quick single-lesson path alive so this does not regress
  interactive teaching.
- Risk guarded against: if `teach` had been made a pure delegator, the standalone quick-draft
  path would break. The boundary keeps `teach` capable of drafting while making
  `generate-topic` the authority on the complete, verified path.
