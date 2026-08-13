import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

export function EdgeLayer({ edges, width, height }) {
  return html`
    <svg class="edge-layer" width=${width} height=${height}>
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0,8 3,0 6" fill="var(--text-faint)" />
        </marker>
      </defs>
      ${edges.map(points => {
        let d = `M ${points[0].x} ${points[0].y}`;
        for (let i = 1; i < points.length - 1; i++) {
          const cp = points[i];
          const next = points[i + 1];
          d += ` Q ${cp.x} ${cp.y} ${(cp.x + next.x) / 2} ${(cp.y + next.y) / 2}`;
        }
        const last = points[points.length - 1];
        d += ` L ${last.x} ${last.y}`;
        return html`<path d=${d} fill="none" stroke="var(--border)" stroke-width="1.5" marker-end="url(#arrowhead)" />`;
      })}
    </svg>
  `;
}
