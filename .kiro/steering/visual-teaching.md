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

Colors are defined as CSS custom properties in `assets/style.css` (light + dark variants). Use `var(--svg-*)` in inline SVGs — never hardcode hex.

| Color | Meaning | Variable (stroke) | Variable (fill) | Variable (text) |
|-------|---------|-------------------|-----------------|-----------------|
| Blue | Primary component, input, the thing being discussed | `--svg-primary` | `--svg-primary-fill` | `--svg-primary-text` |
| Green | Success, output, healthy state | `--svg-success` | `--svg-success-fill` | `--svg-success-text` |
| Amber | Warning, caution, operational concern | `--svg-warning` | `--svg-warning-fill` | `--svg-warning-text` |
| Red | Error, anti-pattern, problem | `--svg-error` | `--svg-error-fill` | `--svg-error-text` |
| Gray | Infrastructure, neutral, supporting | `--svg-neutral` | `--svg-neutral-fill` | `--svg-neutral-text` |

Additional variables: `--svg-line` (connector lines), `--svg-text` (general text).

Light mode resolves to the original hex values (blue=#2563eb, green=#16a34a, etc.). Dark mode resolves to lighter/desaturated variants appropriate for dark backgrounds.

## Diagram Selection

| Content type | Tool | Command |
|-------------|------|---------|
| Architecture layers | `draw-diagram.py --type stack` | Vertical layered stack |
| Data/request flows | `draw-diagram.py --type flow` | Left-to-right pipeline |
| Service maps | `draw-diagram.py --type hub` | Central hub with radial spokes |
| Fan-out/fan-in, dependency graphs (≤8 nodes) | `draw-diagram.py --type graph` | Auto-ranked nodes with edges, groups |
| Cyclic graphs, state machines, 9+ nodes | `draw-diagram.py --type graph --backend graphviz` | Auto-layout via Graphviz (dot/neato/fdp) |
| Network topologies (undirected) | `draw-diagram.py --type graph --backend graphviz --engine neato` | Force-directed layout |
| Custom layout, annotated detail | Raw inline SVG | Use patterns from `assets/svg-patterns.md` |
| Sequence diagrams (multi-actor message flows) | D2 CLI | `d2 input.d2 output.svg` |
| Step-by-step buildup of a diagram | Progressive reveal | `data-step` attrs + `assets/progressive-reveal.js` |

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
- Use `draw-diagram.py` for standard types — outputs accessible, responsive SVG to stdout
- For complex auto-layout (sequence diagrams, state machines), use D2: `d2 input.d2 output.svg`
- Render `.mmd`/`.d2` batch files with `tools/render-diagrams.sh` (outputs to `assets/generated/`)

## Single-Axis Preferences

When adding user preferences to the reading panel, each control should modify ONE behavior axis — not introduce modal switching. Apply this when:

- A proposed toggle would change the DOM structure (e.g., "Flow vs Sections" was wrong; "start collapsed" was right)
- A proposed mode switch can be decomposed into independent booleans (e.g., "cards + collapsible" is two axes, not one mode)
- Two options share most behavior and differ only in a default value (that's a preference, not a mode)

Don't apply this to genuinely distinct page types (map page vs lesson page) or features that require coordinated multi-property changes (theme dark/light is one axis despite changing many CSS vars).
