---
id: "135"
title: "Research: chunking strategies, provenance tracking, and multi-source synthesis for doc-based learning"
status: open
blocked_by: []
priority: high
---

# Research: chunking strategies, provenance tracking, and multi-source synthesis

## What to research

Dispatch subagents to investigate these topics in parallel:

1. **Document chunking for learning** — How to split a PDF/book into teachable units. Semantic chunking vs heading-based vs fixed-size. How RAG systems chunk vs how learning systems should chunk (different goals). Overlap strategies. Handling figures, tables, code blocks.

2. **Provenance tracking in educational content** — How to trace generated questions/lessons back to specific source passages. Citation formats for page-level vs section-level attribution. How Rustacean Academy's "Could They Answer This?" gate works in practice. Verification workflows.

3. **Multi-source synthesis** — How coding-best-practices handles conflicting sources. The "compound don't duplicate" pattern. When to surface disagreement as learning content vs when to resolve it. How to merge perspectives without losing attribution.

4. **Cognitive load separation** — Research on sequencing base concepts vs nuance/exceptions. Rustacean Academy's "best practices deferred to review" pattern. Optimal timing for introducing conflicting perspectives (after base understanding, not during).

5. **Source fidelity vs pedagogical transformation** — The spectrum from "teach the doc exactly" to "use the doc as research input." Where teach-me should sit. When to add analogies/diagrams that go beyond the source material.

## Acceptance criteria

- [ ] Findings for all 5 topics written to .scratch/research/
- [ ] Each finding includes: summary, key patterns, sources cited, open questions
- [ ] Cross-cutting synthesis: which patterns reinforce each other, which conflict
- [ ] Concrete recommendations for teach-me's implementation approach
