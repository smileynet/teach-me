---
id: "138"
title: "Spike: auto-generating MAP.md from document structure — heading hierarchy vs semantic clustering"
status: open
blocked_by: ["135"]
---

# Spike: MAP.md generation from document structure

## Question to answer

Given a chunked document, what's the best way to generate a MAP.md that teaches the material effectively? Two competing approaches:

- **Heading hierarchy**: Document's own structure (chapters → sections → topics). Respects author's intended order.
- **Semantic clustering**: Group chunks by concept similarity, reorder by prerequisite dependency. May disagree with document order.

## Approach

1. Take one well-structured doc (e.g., a Rust book chapter) and generate MAP.md both ways
2. Evaluate: Does heading-based order produce a learnable sequence? Does semantic clustering improve on it?
3. Test hybrid: Use heading structure as base, reorder only when prerequisite analysis suggests a different order
4. Define heuristics: when to trust document order vs when to override

## Acceptance criteria

- [ ] Two MAP.md outputs for same source (heading-based vs semantic)
- [ ] Human evaluation: which produces better learning flow?
- [ ] Decision: default approach + when to override
- [ ] Working script that generates MAP.md from chunk index
