# SVG Diagram Patterns

Reusable inline SVG patterns for teaching diagrams. Read this before writing any lesson — use these patterns rather than inventing new ones each time.

## Design Rules

- Max 5-9 elements per diagram
- Labels go ON the diagram (never separate)
- One-line verbal summary above every diagram
- Consistent colors: blue (#2563eb) = primary/input, green (#16a34a) = success/output, amber (#d97706) = warning/caution, gray (#6b7280) = neutral/infrastructure
- Font: `font-family="system-ui, sans-serif"` at `font-size="13"` or `14`
- Rounded corners: `rx="6"` on all rects
- Arrow markers: define once, reuse via `marker-end="url(#arrow)"`

## Arrow Marker Definition

Include this once per SVG that uses arrows:

```svg
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#374151"/>
  </marker>
</defs>
```

## Pattern: Layered Stack (Architecture)

Use for: showing layers/tiers of a system (e.g., catalog → metadata → data)

```svg
<svg viewBox="0 0 320 220" xmlns="http://www.w3.org/2000/svg">
  <rect x="60" y="10" width="200" height="50" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="160" y="40" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Layer 1 (Top)</text>

  <rect x="60" y="80" width="200" height="50" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="160" y="110" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Layer 2 (Middle)</text>

  <rect x="60" y="150" width="200" height="50" rx="6" fill="#f3f4f6" stroke="#6b7280" stroke-width="1.5"/>
  <text x="160" y="180" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Layer 3 (Bottom)</text>

  <line x1="160" y1="60" x2="160" y2="80" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="160" y1="130" x2="160" y2="150" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>
</svg>
```

## Pattern: Flow (Left to Right)

Use for: data pipelines, request flows, sequential processes

```svg
<svg viewBox="0 0 500 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
      markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#374151"/>
    </marker>
  </defs>

  <rect x="10" y="15" width="120" height="50" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="70" y="45" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13">Source</text>

  <line x1="130" y1="40" x2="180" y2="40" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>

  <rect x="185" y="15" width="120" height="50" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
  <text x="245" y="45" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13">Process</text>

  <line x1="305" y1="40" x2="355" y2="40" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>

  <rect x="360" y="15" width="120" height="50" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="420" y="45" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13">Output</text>
</svg>
```

## Pattern: Side-by-Side Comparison

Use for: before/after, option A vs B, problem/solution

```svg
<svg viewBox="0 0 500 160" xmlns="http://www.w3.org/2000/svg">
  <!-- Left: Before -->
  <rect x="10" y="10" width="220" height="140" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4"/>
  <text x="120" y="35" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#dc2626" font-weight="600">BEFORE</text>
  <text x="120" y="80" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13">Content here</text>

  <!-- Right: After -->
  <rect x="270" y="10" width="220" height="140" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
  <text x="380" y="35" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#16a34a" font-weight="600">AFTER</text>
  <text x="380" y="80" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13">Content here</text>

  <!-- Arrow between -->
  <text x="248" y="85" text-anchor="middle" font-family="system-ui, sans-serif" font-size="20">→</text>
</svg>
```

## Pattern: Annotated Box (Component Detail)

Use for: zooming into one component with callout annotations

```svg
<svg viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
  <!-- Main component -->
  <rect x="120" y="40" width="160" height="80" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="200" y="75" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Component</text>
  <text x="200" y="95" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" fill="#6b7280">subtitle</text>

  <!-- Callout left -->
  <line x1="120" y1="60" x2="30" y2="30" stroke="#6b7280" stroke-width="1" stroke-dasharray="3"/>
  <text x="10" y="25" font-family="system-ui, sans-serif" font-size="11" fill="#6b7280">annotation 1</text>

  <!-- Callout right -->
  <line x1="280" y1="100" x2="350" y2="150" stroke="#6b7280" stroke-width="1" stroke-dasharray="3"/>
  <text x="340" y="168" font-family="system-ui, sans-serif" font-size="11" fill="#6b7280">annotation 2</text>
</svg>
```

## Pattern: Hub-and-Spoke (Central + Connections)

Use for: showing one central service with multiple connected services

```svg
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
      markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#374151"/>
    </marker>
  </defs>

  <!-- Center hub -->
  <rect x="140" y="110" width="120" height="60" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="200" y="145" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Hub</text>

  <!-- Top spoke -->
  <rect x="150" y="20" width="100" height="40" rx="6" fill="#f3f4f6" stroke="#6b7280" stroke-width="1.5"/>
  <text x="200" y="45" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12">Spoke 1</text>
  <line x1="200" y1="60" x2="200" y2="110" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Left spoke -->
  <rect x="10" y="120" width="100" height="40" rx="6" fill="#f3f4f6" stroke="#6b7280" stroke-width="1.5"/>
  <text x="60" y="145" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12">Spoke 2</text>
  <line x1="110" y1="140" x2="140" y2="140" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Right spoke -->
  <rect x="290" y="120" width="100" height="40" rx="6" fill="#f3f4f6" stroke="#6b7280" stroke-width="1.5"/>
  <text x="340" y="145" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12">Spoke 3</text>
  <line x1="260" y1="140" x2="290" y2="140" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Bottom spoke -->
  <rect x="150" y="220" width="100" height="40" rx="6" fill="#f3f4f6" stroke="#6b7280" stroke-width="1.5"/>
  <text x="200" y="245" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12">Spoke 4</text>
  <line x1="200" y1="170" x2="200" y2="220" stroke="#374151" stroke-width="1.5" marker-end="url(#arrow)"/>
</svg>
```
