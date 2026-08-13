import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

/**
 * GenerationStream — shows live output from an SSE generation stream.
 * 
 * Props:
 *   stream — object from createGenerationStream() with status, lines, phase, error signals
 */
export function GenerationStream({ stream }) {
  if (!stream) return null;
  const { status, lines, phase, error } = stream;

  if (status.value === 'idle') return null;

  return html`
    <div class="gen-stream">
      <div class="gen-stream-header">
        ${status.value === 'connecting' && html`<span class="gen-status connecting">Connecting...</span>`}
        ${status.value === 'streaming' && html`<span class="gen-status streaming">Generating${phase.value ? ': ' + phase.value : '...'}</span>`}
        ${status.value === 'done' && html`<span class="gen-status done">✓ Complete</span>`}
        ${status.value === 'error' && html`<span class="gen-status error">✗ ${error.value || 'Failed'}</span>`}
      </div>
      ${lines.value.length > 0 && html`
        <div class="gen-stream-output">
          ${lines.value.slice(-20).map(l => html`
            <div class=${l.phase ? 'line phase-' + l.phase.split(':')[0] : 'line'}>${l.text || ''}</div>
          `)}
        </div>
      `}
    </div>
  `;
}

/**
 * GenerationModal — overlay that shows generation progress and auto-closes.
 *
 * Props:
 *   stream — object from createGenerationStream()
 *   onClose — callback when user dismisses
 *   onComplete — callback when generation finishes (e.g., reload page)
 */
export function GenerationModal({ stream, onClose, onComplete }) {
  if (!stream || stream.status.value === 'idle') return null;

  function handleClose() {
    if (stream.status.value === 'streaming' || stream.status.value === 'connecting') {
      stream.cancel();
    }
    if (onClose) onClose();
  }

  // Auto-complete after done
  if (stream.status.value === 'done' && onComplete) {
    setTimeout(onComplete, 1500);
  }

  return html`
    <div class="gen-modal-overlay" onClick=${e => { if (e.target === e.currentTarget) handleClose(); }}>
      <div class="gen-modal">
        <${GenerationStream} stream=${stream} />
        <div class="gen-modal-actions">
          ${(stream.status.value === 'streaming' || stream.status.value === 'connecting') && html`
            <button class="btn" onClick=${() => stream.cancel()}>Cancel</button>
          `}
          ${(stream.status.value === 'done' || stream.status.value === 'error') && html`
            <button class="btn" onClick=${handleClose}>Close</button>
          `}
        </div>
      </div>
    </div>
  `;
}
