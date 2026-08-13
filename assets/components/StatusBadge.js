import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

export function StatusBadge({ status }) {
  const label = {
    'not-started': 'not started',
    'generating': 'generating…',
    'complete': '✓ complete',
    'in-progress': 'in progress'
  }[status.value] || status.value;

  return html`<span class="badge ${status.value}">${label}</span>`;
}
