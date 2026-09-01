// IteratedMapView (#283) — the domain forest (secondary "Map" view of the aggregate, #276):
// delegates layout to the unified GraphView, injecting a static domain <a> card. Domain-level
// config: nodeKey=slug, viewport='fit', hover=true, edge styles (parent solid gray, leads_to
// dashed accent). Legend + islands tray stay caller-side chrome outside the graph.
import { h } from 'preact';
import htm from 'htm';
import { GraphView } from './GraphView.js';

const html = htm.bind(h);
const CARD_W = 300;

function Ring({ complete, total }) {
  const pct = total > 0 ? complete / total : 0, r = 14, c = 2 * Math.PI * r, off = c * (1 - pct);
  const color = pct >= 1 ? 'var(--success)' : pct > 0 ? 'var(--accent)' : 'var(--text-muted)';
  return html`<span class="dc-ring" aria-hidden="true"><svg width="34" height="34" viewBox="0 0 34 34">
    <circle cx="17" cy="17" r=${r} fill="none" stroke="var(--border)" stroke-width="3"/>
    <circle cx="17" cy="17" r=${r} fill="none" stroke=${color} stroke-width="3" stroke-dasharray=${c} stroke-dashoffset=${off} transform="rotate(-90 17 17)" stroke-linecap="round"/>
    <text x="17" y="21" text-anchor="middle" font-size="10" fill="var(--text-muted)">${complete}/${total}</text></svg></span>`;
}

// parent = structural (solid gray + arrow); leads_to = navigational (dashed accent + arrow).
const DOMAIN_EDGE_STYLES = {
  parent: { stroke: 'var(--text-muted)', dashed: false, arrow: true },
  leads_to: { stroke: 'var(--accent)', dashed: true, arrow: true },
};

export function IteratedMapView({ domains, edges, islands }) {
  const islandSet = new Set(islands || []);
  const graphDomains = domains.filter(d => !islandSet.has(d.slug));
  const byslug = Object.fromEntries(domains.map(d => [d.slug, d]));

  const renderNode = (d, position, ui) => html`
    <a key=${d.slug} class=${'im-card' + (d.depth > 0 ? ' is-child' : '')} href=${d.mapHref}
       data-domain=${d.slug}
       style="position:absolute;left:${position.x}px;top:${position.y}px;width:${CARD_W}px;opacity:${ui.dimmed ? 0.25 : 1}"
       onMouseEnter=${() => ui.setHover(d.slug)} onMouseLeave=${() => ui.setHover(null)}
       onFocus=${() => ui.setHover(d.slug)} onBlur=${() => ui.setHover(null)}>
      <h3>${d.title}${d.depth > 0 && html`<span class="dc-sub-badge">sub-map</span>`}</h3>
      <div class="dc-meta"><${Ring} complete=${d.complete} total=${d.total} /> ${d.total} topics${d.inProgress ? `, ${d.inProgress} in progress` : ''}</div>
    </a>`;

  return html`<div class="iterated-map">
    <div class="im-legend">
      <span><svg width="34" height="10" aria-hidden="true"><line x1="2" y1="5" x2="32" y2="5" stroke="var(--text-muted)" stroke-width="2"/></svg> contains (sub-map)</span>
      <span><svg width="34" height="10" aria-hidden="true"><line x1="2" y1="5" x2="32" y2="5" stroke="var(--accent)" stroke-width="2" stroke-dasharray="5 3"/></svg> leads to</span>
    </div>
    <${GraphView}
      nodes=${graphDomains}
      edges=${edges}
      nodeKey=${d => d.slug}
      renderNode=${renderNode}
      viewport="fit"
      hover=${true}
      edgeStyles=${DOMAIN_EDGE_STYLES}
      cardWidth=${CARD_W}
      graphOpts=${{ edgeLabelSpace: false }}
      canvasClass="im-canvas"
      edgeLayerClass="im-edges"
    />
    ${islandSet.size > 0 && html`<div class="islands-panel"><h2>Standalone domains</h2><ul>
      ${[...islandSet].map(s => byslug[s]).filter(Boolean).map(d => html`<li><a href=${d.mapHref}>${d.title} (${d.complete}/${d.total})</a></li>`)}</ul></div>`}
  </div>`;
}
