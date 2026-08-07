---
id: "005"
title: "Research: visual tooling open questions"
status: done
priority: medium
blocked_by: []
type: research
---

# Research: visual tooling open questions

## Questions to investigate

### Mermaid MCP viability
- Does the official Mermaid Chart MCP (`https://mcp.mermaid.ai/mcp`) actually work with kiro-cli?
- What auth is required? Free tier limits?
- Latency for a single diagram render (acceptable for teaching flow?)

### Declarative diagram DSL design
- Is operator overloading (`>>` for connections) worth the complexity vs. a simple function-call API?
- How do mingrammer/diagrams handle auto-layout without Graphviz? (Answer: they don't — they require Graphviz)
- Can we do simple grid-based auto-layout in pure Python (no Graphviz)?

### svg.py vs drawsvg (informed by spikes)
- After spike 001: is drawsvg's marker boilerplate acceptable, or is svg.py's explicit approach better for agent generation?
- Which produces more readable generated code?

### Browser rendering of inline SVG
- Do all target browsers handle `<svg>` inline in HTML without issues?
- Any gotchas with font rendering in inline SVG across platforms?
- Does `viewBox` scaling work reliably for responsive diagrams?

### Teaching component patterns
- What quiz/interaction patterns do other HTML-based courses use (Jupyter Book, mdBook, Docusaurus)?
- Are there accessibility requirements we're missing for interactive components?

## Output

Write findings to `.scratch/research/visual-open-questions.md` as answers are found (append incrementally).
