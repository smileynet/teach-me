---
id: "032"
title: "Feature: open-ended knowledge and interests analysis from SR + dialog"
status: done
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Feature: open-ended knowledge and interests analysis from SR + dialog

## What to build

Periodically generate an open-ended analysis of what the learner knows, what they're curious about, and where their understanding is developing — based on the full picture (SR data, Socratic conversations, questions asked, tangents explored), not just card pass/fail rates.

## Why

SR data tells you "this card was recalled at 4-day intervals." That's useful for scheduling but doesn't capture the shape of understanding. A learning record should say things like:

- "Understands Iceberg's metadata tree deeply — can explain the WHY of each layer"
- "Interested in query performance optimization — keeps asking about pruning"
- "Conflates snapshots and branches — the git analogy may be causing confusion here"
- "Starting to think about operational concerns (compaction, maintenance) — ready for next lesson"

This is a qualitative synthesis the agent writes, informed by (but not reduced to) SR metrics.

## Design

**Inputs (what informs the analysis):**
- SR card performance (what's strong, what's leeching, what patterns emerge)
- Socratic gate conversations (what the learner explained well, where they hesitated)
- Questions the learner asked during lessons (curiosity signals)
- Exercise attempts and hints used
- Time between sessions (engagement pattern)

**Output:**
- `learning-records/NNNN-knowledge-snapshot-<date>.md` — periodic synthesis
- Written in natural language, not metrics tables
- Structured as: "Demonstrated understanding", "Developing understanding", "Interests and curiosity", "Potential confusions to watch"

**Trigger:**
- After every 3-5 lessons (not every session — needs enough signal)
- On explicit request ("what do I know?", "where am I?")
- When significant SR events occur (concept reaches mastery, or leeching pattern detected)

## What this is NOT

- Not a report card or grade
- Not a raw dump of SR statistics
- Not a blocker to progression (see ticket 031)
- Not a replacement for learning records — it's a new TYPE of learning record (knowledge snapshot vs. demonstrated-understanding from Socratic gate)

## Open questions

- How much should SR data weight vs. conversational signals?
- Should the analysis propose what to teach next, or just describe current state?
- How to detect "interest signals" from lesson interactions?
- Should old snapshots be superseded or kept as a timeline?

## Acceptance criteria

- [x] Agent can generate a knowledge snapshot from available signals
- [x] Snapshot is qualitative and open-ended, not just metrics
- [x] Covers: demonstrated knowledge, developing areas, interests, potential confusions
- [x] Written as a learning record (not ephemeral)
- [x] teach skill reads snapshots when calculating ZPD for next lesson
- [x] Does not gate or block — purely informational for the agent and learner

## Resolution (closed 2026-08-10)

Shelved. teach-me is a casual learning/exploration tool, not a retention optimization system. Deep knowledge analysis (fragile card detection, curiosity inference, dialog-informed KC tracing) solves a problem the user doesn't have. The SR system reinforces things worth remembering — it doesn't need a meta-layer analyzing how well retention is working. If the use case shifts toward deliberate mastery, revisit Phase 1 (stability health + Bloom's gaps) from the proposal at `.scratch/proposals/032-knowledge-analysis-proposal.md`.
