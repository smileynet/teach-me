---
id: "055"
title: "Spike: cross-domain link emergence — when to surface connections between maps"
status: open
priority: low
blocked_by: []
type: spike
---

# Spike: cross-domain link emergence

## Question to answer

When a learner explores multiple unrelated domains, natural connections sometimes emerge (e.g., "data governance" appears in both analytics and security). When should the system notice this, and how should it surface it without forcing relationships?

## Design principles (from research)

- **Sparingly** — only when the connection is genuine, useful, and timely
- **Never during instruction** — surface during review or at completion, not mid-lesson
- **Suggest, don't assert** — "This connects to your work in [other domain]" not "These are related"
- **Learner has depth in both** — don't link to a domain the learner hasn't explored

## Three minimal mechanisms to test

### 1. Glossary `also_in` field
When the same term appears in two domain glossaries, note it:
```json
{"term": "data governance", "also_in": ["web-security", "data-analytics"]}
```

### 2. Tag/concept overlap detection
At `sr:analytics` time, detect when SR cards from different domains share tags. If overlap > 3 cards with shared tags → note the connection.

### 3. leads_to intersection
If domain A's `leads_to` includes a slug that domain B already covers → that's a confirmed connection.

## What to build in the spike

A simple script that scans all MAP.md files + JSONL question banks and reports potential cross-domain connections:

```bash
mise run map:connections
# Output:
# ⚡ Potential connections:
#   "data governance" — appears in: data-analytics (topic), web-security (topic)
#   Tag overlap: "concurrency" — 3 cards in data-analytics, 2 cards in distributed-systems
#   leads_to match: data-analytics leads_to "data-governance-at-scale" ← web-security covers "governance"
```

## What NOT to build

- No automatic link injection into pages
- No recommendation engine
- No forced "related domains" section on index page
- No bidirectional wiki-style backlinks

## Success criteria

- [ ] Detection script identifies genuine cross-domain connections
- [ ] Produces < 5 connections across 3 test domains (sparse, not spammy)
- [ ] Evaluate: are the detected connections actually useful to a learner?
- [ ] Decision: should these surface in the UI, or just inform the teach skill's conversation?
