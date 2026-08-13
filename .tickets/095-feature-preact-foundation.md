---
id: "095"
title: "Preact foundation: vendor deps, import map, shared components"
type: feature
status: done
priority: high
blocked_by: []
---

# Preact foundation: vendor deps, import map, shared components

## What to build

The shared infrastructure all Preact pages will import: vendored dependencies, import map template, and core reusable components.

## Architecture (from research)

**Data Island pattern:** Python generators emit a static Preact shell + JSON data block. Preact reads the data at runtime. No template string interpolation of JS code.

```html
<script type="application/json" id="page-data">{"topics": [...], "edges": [...]}</script>
<script type="module">
  import { render } from 'preact';
  import { MapView } from './components/MapView.js';
  const data = JSON.parse(document.getElementById('page-data').textContent);
  render(html`<${MapView} ...${data} />`, document.getElementById('app'));
</script>
```

## Deliverables

### 1. Vendor dependencies (`assets/vendor/`)
Download and self-host (LAN-first, no CDN dependency at runtime):
- `preact.module.js` (~4KB gzip)
- `preact-signals.module.js` (~1.6KB)
- `htm.module.js` (~1KB)
- `dagre.min.js` (~30KB)

### 2. Import map template (`assets/import-map.json`)
```json
{
  "imports": {
    "preact": "./assets/vendor/preact.module.js",
    "preact/": "./assets/vendor/preact/",
    "preact/hooks": "./assets/vendor/preact-hooks.module.js",
    "@preact/signals": "./assets/vendor/preact-signals.module.js",
    "htm": "./assets/vendor/htm.module.js"
  }
}
```

### 3. Core components (`assets/components/`)
- `TopicCard.js` — title, why, prereq label, status badge, action buttons
- `StatusBadge.js` — reactive badge (not-started / generating / complete)
- `GenButton.js` — generate button that triggers SSE and shows progress
- `EdgeLayer.js` — SVG overlay rendering dagre edge paths
- `store.js` — module-level signals for topic states, generation status

### 4. Page shell helper (`tools/lib/preact_page.py`)
Python helper that generates the HTML boilerplate:
- Import map script tag (with correct relative paths)
- Data island script tag (serialized JSON)
- Mount point div
- CSS link to style.css
- Theme toggle script

## Acceptance Criteria

- [ ] `assets/vendor/` contains all 4 deps, loadable offline
- [ ] Import map resolves correctly from `lessons/` subdirectory (relative paths)
- [ ] Each component in `assets/components/` exports a named function
- [ ] Components use signals from `store.js` for shared state
- [ ] `preact_page.py` helper generates valid HTML that renders components
- [ ] Existing pages still work (no breakage from adding new files)
- [ ] `mise run verify` passes

## Research references

- `.scratch/research/preact-no-build-patterns.md` — project structure
- `.scratch/research/preact-component-library-cdn.md` — individual files, signal stores
- `.scratch/research/python-to-preact-templating.md` — data island pattern
- `.scratch/research/asset-management-no-bundler.md` — vendor locally for LAN
