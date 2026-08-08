# Visual Teaching Guidelines

When creating lessons with diagrams or visual aids, follow these evidence-based rules.

## Core Principles (Mayer, Paivio, Sweller)

1. **Every visual has an instructional purpose.** No decoration. If removing it wouldn't hurt understanding, remove it. (Coherence principle, d=0.70)
2. **Labels go ON the diagram.** Never separate a visual from its explanation. (Spatial contiguity, d=0.79)
3. **5-9 elements max per diagram.** Break complex systems into progressive layers. (Cognitive load theory)
4. **Dual code everything.** Every diagram has a one-line verbal summary above it. (Dual coding, Paivio 1986)
5. **Consistent visual vocabulary.** Same color/shape means same thing across ALL lessons. (Signaling principle, d=0.46)
6. **Static over animated.** Animation only for inherently temporal processes. (Tversky et al., 2002)

## Color Vocabulary

| Color | Meaning | Hex |
|-------|---------|-----|
| Blue | Primary component, input, the thing being discussed | #2563eb / fill #dbeafe |
| Green | Success, output, healthy state | #16a34a / fill #dcfce7 |
| Amber | Warning, caution, operational concern | #d97706 / fill #fef3c7 |
| Red | Error, anti-pattern, problem | #dc2626 / fill #fef2f2 |
| Gray | Infrastructure, neutral, supporting | #6b7280 / fill #f3f4f6 |

## Diagram Selection

| Content type | Use |
|-------------|-----|
| Architecture layers | Inline SVG layered stack |
| Data/request flows | Inline SVG flow or Mermaid sequence |
| Decision processes | Mermaid flowchart |
| State machines | Mermaid state diagram |
| Component relationships | Inline SVG hub-and-spoke |
| Comparisons | Inline SVG side-by-side |

## Anti-Patterns (DO NOT)

- Decorative images that don't teach (increases cognitive load, PMC 2024)
- Diagram on one part of the page, explanation on another (split-attention effect)
- Text that merely restates what the visual shows (redundancy principle)
- Complex diagrams with 10+ elements at one level (overloads working memory)
- Inconsistent colors/shapes between lessons
- D2 sketch mode for inline SVGs (3-4x file size: 78-98KB vs 19-26KB normal mode — use normal mode by default, sketch only for standalone files where approachability outweighs size)

## Accessibility (WCAG 2.1 compliance)

Every informative SVG requires:
- `role="img"` on the `<svg>` element
- `<title>` as first child with a brief description of what the diagram shows
- `aria-labelledby` linking to the title's ID
- `viewBox` only (no fixed width/height) — responsive scaling via CSS `max-width:100%; height:auto`

**Color independence:** Do not rely on color alone to convey meaning. Every color-coded element must also have a text label. The color vocabulary reinforces meaning — it does not carry it.

**Progressive reveal accessibility:** When using `data-step` for step-through diagrams, ensure `aria-live="polite"` on the container so screen readers announce new content as steps advance.

**The `--title` flag on draw-diagram.py handles all of the above automatically.** For hand-written SVGs, follow the accessibility pattern in `assets/svg-patterns.md`.

## Implementation

- Read `assets/svg-patterns.md` for reusable SVG snippets
- Inline SVG directly in lesson HTML (zero dependencies)
- For standard diagram types (sequence, flowchart), write Mermaid source and render with `tools/render-diagrams.sh` if available
