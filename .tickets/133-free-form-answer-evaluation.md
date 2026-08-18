---
id: "133"
title: "Feature: free-form text answer with AI evaluation against criteria"
status: open
blocked_by: []
priority: low
---

# Feature: free-form text answer with AI evaluation against criteria

## Context

Post-release feature. Currently users self-assess (Got it / Partial / Missed) after seeing the criteria. This adds an optional text box where the user types their answer BEFORE reveal, then the server evaluates it against the numbered criteria and gives specific feedback on what they hit and missed.

## What to build

- Text area below each open-answer prompt ("Type your answer...")
- On submit, POST to server endpoint with user's text + question criteria
- Server uses LLM to evaluate: which criteria points were addressed, which missed
- Returns per-point feedback (✓ mentioned / ✗ not addressed / ◐ partial)
- Shows alongside the criteria checklist as a personalized assessment
- Falls back to manual self-assessment when server unavailable (static/offline)

## Design considerations

- Must not block the reveal flow — user can always skip and self-assess
- Evaluation should be encouraging (Duolingo-style: celebrate what was right)
- Response time target: <3s for evaluation
- Privacy: user text stays on local server, not sent externally unless configured

## Acceptance criteria

- [ ] Text area appears below open-answer prompts (optional — skip button available)
- [ ] Server endpoint evaluates user text against criteria points
- [ ] Per-criterion feedback rendered (hit/miss/partial with explanation)
- [ ] Graceful fallback to self-assessment when server unavailable
- [ ] Works on lesson quiz pages and SR review cards
