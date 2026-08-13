import { signal, batch } from '@preact/signals';

/**
 * SSE Generation Stream Service
 * 
 * Standalone signal service (not a hook) — any component can subscribe.
 * Creates an EventSource connection to /api/generate, streams output
 * lines into signals, handles reconnection with exponential backoff.
 * 
 * Usage:
 *   import { createGenerationStream } from '../services/generation.js';
 *   const stream = createGenerationStream('teach me about X');
 *   stream.start();
 *   // stream.status.value → 'idle' | 'connecting' | 'streaming' | 'done' | 'error'
 *   // stream.lines.value → [{text, phase}, ...]
 *   // stream.phase.value → current phase string
 *   stream.cancel();
 */

const MAX_RETRIES = 3;
const BASE_DELAY = 1000;
const MAX_DELAY = 30000;

export function createGenerationStream(prompt) {
  const status = signal('idle');
  const lines = signal([]);
  const phase = signal('');
  const error = signal('');

  let es = null;
  let taskId = null;
  let retryCount = 0;
  let retryTimeout = null;

  function start() {
    if (status.value === 'streaming' || status.value === 'connecting') return;

    status.value = 'connecting';
    error.value = '';
    lines.value = [];
    phase.value = '';

    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, mock: false })
    })
      .then(r => {
        if (!r.ok) throw new Error(`Server error: ${r.status}`);
        return r.json();
      })
      .then(data => {
        taskId = data.id;
        connectSSE(data.stream_url);
      })
      .catch(err => {
        error.value = err.message || 'Could not connect to server';
        status.value = 'error';
      });
  }

  function connectSSE(streamUrl) {
    es = new EventSource(streamUrl);
    status.value = 'streaming';
    retryCount = 0;

    es.addEventListener('line', e => {
      try {
        const line = JSON.parse(e.data);
        batch(() => {
          lines.value = [...lines.value, line];
          if (line.phase) phase.value = line.phase;
        });
      } catch (err) {
        // Non-JSON line, ignore
      }
    });

    es.addEventListener('done', () => {
      cleanup();
      status.value = 'done';
    });

    es.onerror = () => {
      cleanup();
      if (retryCount < MAX_RETRIES) {
        scheduleRetry();
      } else {
        error.value = 'Connection lost after retries';
        status.value = 'error';
      }
    };
  }

  function scheduleRetry() {
    retryCount++;
    const delay = Math.min(BASE_DELAY * Math.pow(2, retryCount - 1) + Math.random() * 500, MAX_DELAY);
    status.value = 'connecting';
    error.value = `Reconnecting (attempt ${retryCount}/${MAX_RETRIES})...`;
    retryTimeout = setTimeout(() => {
      if (taskId) {
        connectSSE(`/api/generate/${taskId}/stream`);
      } else {
        status.value = 'error';
        error.value = 'Lost task ID, cannot reconnect';
      }
    }, delay);
  }

  function cancel() {
    cleanup();
    if (taskId) {
      fetch(`/api/generate/${taskId}/cancel`, { method: 'POST' }).catch(() => {});
      taskId = null;
    }
    status.value = 'idle';
    error.value = '';
  }

  function cleanup() {
    if (es) {
      es.close();
      es = null;
    }
    if (retryTimeout) {
      clearTimeout(retryTimeout);
      retryTimeout = null;
    }
  }

  function reset() {
    cleanup();
    taskId = null;
    status.value = 'idle';
    lines.value = [];
    phase.value = '';
    error.value = '';
    retryCount = 0;
  }

  return { status, lines, phase, error, start, cancel, reset };
}
