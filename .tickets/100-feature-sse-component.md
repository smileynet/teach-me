---
id: "100"
title: "Shared SSE generation stream component"
type: feature
status: done
priority: high
blocked_by: ["095"]
work_order: 1
tags: [platform]
---

# Shared SSE generation stream component

## What to build

A reusable Preact component + signal service for live generation via SSE. Used by map page, lesson pages, anywhere generation can be triggered.

## Architecture (from research)

**Standalone signal service** (not a hook):
```js
// assets/services/generation.js
import { signal, batch } from '@preact/signals';

export function createGenerationStream(prompt) {
  const status = signal('idle');      // idle | connecting | streaming | done | error
  const lines = signal([]);
  const phase = signal('');
  
  let es = null;
  
  function start() {
    status.value = 'connecting';
    fetch('/api/generate', { method: 'POST', body: JSON.stringify({ prompt, mock: false }) })
      .then(r => r.json())
      .then(data => {
        es = new EventSource(data.stream_url);
        status.value = 'streaming';
        es.addEventListener('line', e => {
          const line = JSON.parse(e.data);
          batch(() => {
            lines.value = [...lines.value, line];
            if (line.phase) phase.value = line.phase;
          });
        });
        es.addEventListener('done', () => { es.close(); status.value = 'done'; });
        es.addEventListener('error', () => { es.close(); status.value = 'error'; });
      })
      .catch(() => { status.value = 'error'; });
  }
  
  function cancel() {
    if (es) es.close();
    status.value = 'idle';
  }
  
  return { status, lines, phase, start, cancel };
}
```

**Reconnection:** Exponential backoff with jitter (base 1s, cap 30s, budget 5 retries).

## Deliverables

- `assets/services/generation.js` — signal service (connect, stream, cancel, reconnect)
- `assets/components/GenerationStream.js` — UI component showing live output
- `assets/components/GenerationModal.js` — overlay version for inline triggering

## Acceptance Criteria

- [x] Service connects to `/api/generate`, streams lines via SSE
- [x] Status signal transitions: idle → connecting → streaming → done/error
- [x] Lines accumulate in signal array (batch updates)
- [x] Cancel closes EventSource and resets state
- [x] UI component shows scrollable output with phase coloring
- [x] Modal version auto-closes or reloads on completion
- [x] Reconnection on transient errors (with backoff)
- [x] Cleanup: EventSource closed when component unmounts

## Research references

- `.scratch/research/preact-sse-patterns.md` — standalone service, backoff, batch()
