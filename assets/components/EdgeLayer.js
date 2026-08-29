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
      ${edges.map(edge => {
        // Back-compat: an edge may be a bare points array or {points, type, source, target}.
        const points = Array.isArray(edge) ? edge : edge.points;
        const type = Array.isArray(edge) ? 'prereq' : (edge.type || 'prereq');
        const source = Array.isArray(edge) ? null : edge.source;
        const target = Array.isArray(edge) ? null : edge.target;
        let d = `M ${points[0].x} ${points[0].y}`;
        for (let i = 1; i < points.length - 1; i++) {
          const cp = points[i];
          const next = points[i + 1];
          d += ` Q ${cp.x} ${cp.y} ${(cp.x + next.x) / 2} ${(cp.y + next.y) / 2}`;
        }
        const last = points[points.length - 1];
        d += ` L ${last.x} ${last.y}`;
        // Signaling: 'related' is a softer, symmetric adjacency → dashed, no arrowhead.
        const dashed = type === 'related';
        return html`<path d=${d} fill="none" stroke="var(--border)" stroke-width="1.5"
          stroke-dasharray=${dashed ? '5 4' : 'none'}
          marker-end=${dashed ? 'none' : 'url(#arrowhead)'}
          data-source=${source} data-target=${target} data-type=${type} />`;
      })}
    </svg>
  `;
}
