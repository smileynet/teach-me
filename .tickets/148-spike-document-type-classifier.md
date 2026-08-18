---
id: "148"
title: "Spike: classify document type (tutorial vs reference) from structure signals"
status: open
blocked_by: []
---

# Spike: document type classification

## Question to answer

Can we reliably detect whether a document is tutorial-style (pedagogically ordered — trust it) or reference-style (lookup-ordered — reorganize for learning)?

## Signals to test

| Signal | Tutorial | Reference |
|--------|----------|-----------|
| Heading progression | "Chapter 1, 2, 3..." or narrative flow | Alphabetical, feature-by-feature |
| Section length | Long (prose-heavy, 500-2000 words) | Short (entries, 50-300 words) |
| Forward references | Rare ("as we saw in ch.2") | Common (cross-linking) |
| Code/example density | Increasing with chapter | Uniform throughout |
| Prerequisite language | "Before reading this..." present | Absent |
| First paragraph style | Motivating/contextual | Definitional |

## Approach

1. Compute each signal from chunk_pdf.py output
2. Score document on a tutorial↔reference spectrum (0-1)
3. Test on 4+ documents: textbook, API docs, spec, mixed

## Acceptance criteria

- [ ] Scoring function takes chunk list, returns classification + confidence
- [ ] Correctly classifies 3/4 test documents
- [ ] Documented heuristic (which signals matter most)
- [ ] Edge case: mixed documents (tutorial chapters + reference appendix) handled
