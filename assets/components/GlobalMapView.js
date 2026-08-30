import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import htm from 'htm';
import { DomainCard } from './DomainCard.js';
import { EdgeLayer } from './EdgeLayer.js';

const html = htm.bind(h);

const CARD_WIDTH = 300;
const CARD_PAD = 50;

// Domain-node layout: same dagre engine as MapView.computeLayout, but nodes are DOMAIN
// cards (fixed-ish height) and edges are structural (parent/leads_to). Islands (nodes
// with no edge) are laid out by dagre as separate components; dagre stacks disconnected
// components — acceptable for a small forest, and they're ALSO listed in the sidebar.
function computeLayout(domains, edges) {
  const nodeIds = new Set(domains.map(d => d.slug));
  const graphEdges = (edges || []).filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));

  const g = new dagre.graphlib.Graph({ compound: false });
  g.setGraph({ rankdir: 'TB', nodesep: CARD_PAD, ranksep: 70, marginx: 24, marginy: 24 });
  g.setDefaultEdgeLabel(() => ({}));

  const H = 96; // domain card height (title + ring row)
  domains.forEach(d => g.setNode(d.slug, { width: CARD_WIDTH, height: H }));
  graphEdges.forEach(e => g.setEdge(e.source, e.target, { type: e.type }));

  dagre.layout(g);

  const positions = {};
  domains.forEach(d => {
    const n = g.node(d.slug);
    positions[d.slug] = { x: n.x - CARD_WIDTH / 2, y: n.y - H / 2 };
  });

  const laidEdges = [];
  g.edges().forEach(e => {
    laidEdges.push({ points: g.edge(e).points, type: g.edge(e).type || 'parent', source: e.v, target: e.w });
  });

  const gd = g.graph();
  return { positions, edges: laidEdges, width: gd.width, height: gd.height };
}

export function GlobalMapView({ domains, edges, islands }) {
  const [layout, setLayout] = useState(null);

  useEffect(() => {
    if (!domains || !domains.length) return;
    setLayout(computeLayout(domains, edges));
  }, []);

  if (!layout) return html`<div class="loading">Computing layout…</div>`;

  const byslug = Object.fromEntries(domains.map(d => [d.slug, d]));
  const islandDomains = (islands || []).map(s => byslug[s]).filter(Boolean);

  return html`
    <div>
      <div class="dag-container">
        <div class="dag-canvas" style="width:${layout.width}px;height:${layout.height}px;position:relative"
             data-render-complete="true" data-domain-count=${domains.length} data-edge-count=${layout.edges.length}>
          <${EdgeLayer} edges=${layout.edges} width=${layout.width} height=${layout.height} />
          ${domains.map(d => html`
            <${DomainCard} key=${d.slug} domain=${d} position=${layout.positions[d.slug]} />
          `)}
        </div>
      </div>
      ${islandDomains.length > 0 && html`
        <div class="islands-panel" data-island-count=${islandDomains.length}>
          <h2>Standalone domains (no detected connections)</h2>
          <ul>
            ${islandDomains.map(d => html`
              <li><a href=${d.mapHref} data-domain=${d.slug}>${d.title} (${d.complete}/${d.total})</a></li>
            `)}
          </ul>
        </div>
      `}
    </div>
  `;
}
