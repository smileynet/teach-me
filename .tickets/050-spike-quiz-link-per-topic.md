---
id: "050"
title: "Spike: quiz link per topic on map page — generate or browse"
status: open
priority: medium
blocked_by: []
type: spike
---

# Spike: quiz link per topic on map page

## What to test

Can each topic card on the map page have a "Quiz" action that either links to an existing quick-check page (filtered to that topic) or offers to generate questions?

## Design

On each topic card, alongside "Generate this topic" or "Open lesson →":

```html
<a href="review/quick-check.html?topic=ingestion" class="quiz-link">Quiz →</a>
<!-- or if no questions exist: -->
<button class="generate-btn" onclick="offerGenerateQuiz('ingestion')">Generate quiz</button>
```

## Questions to answer

1. Can quick-check.py accept a topic filter and produce a per-topic page?
   (Currently it filters by topic slug — we'd need one output file per topic, or a URL param approach)
2. Should we generate separate HTML per topic, or one page with JS filtering?
3. What's the UX for "no questions yet" — same modal pattern as lesson generation?
4. How does the map page know if questions exist for a topic? (Check JSONL file at generation time)

## Success criteria

- [ ] Topic cards show quiz link when questions exist for that topic
- [ ] Topic cards show "Generate quiz" when no questions exist
- [ ] Clicking quiz link opens a functional quick-check page for that topic
- [ ] Generation modal shows appropriate CLI command for question generation
