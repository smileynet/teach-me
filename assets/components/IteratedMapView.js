// IteratedMapView — the SECONDARY relationship view of the domain forest (#276).
//
// Plain dagre layout (NOT a hand-rolled grid) + small-graph improvements:
//  1. Responsive FIT-TO-VIEW via a single CSS transform on the canvas wrapper (scale =
//     min(vpW/gW, vpH/gH), clamp ≤ 1). Cards stay HTML <a> nodes (rings/hover/focus) — no
//     SVG viewBox. Text stays crisp; toggling is cheap.
//  2. Edge-type encoding + legend (WCAG 1.4.1 — color paired with a 2nd cue): SOLID gray =
//     contains/parent (structural); DASHED accent = leads_to (navigational); distinct
//     arrowhead markers per type.
//  3. Hover-neighbor-highlight: fade everything not adjacent to the hovered node.
//  Islands (no structural edge) → a sidebar tray, not floating in the canvas.
//
// Reads `window.dagre` (vendored, loaded in <head> via render_index_page(include_dagre=True)).
import { h } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);
const CARD_W = 300, PAD = 40;

function Ring({ complete, total }) {
  const pct = total > 0 ? complete / total : 0, r = 14, c = 2 * Math.PI * r, off = c * (1 - pct);
  const color = pct >= 1 ? 'var(--success)' : pct > 0 ? 'var(--accent)' : 'var(--text-muted)';
  return html`<span class="dc-ring" aria-hidden="true"><svg width="34" height="34" viewBox="0 0 34 34">
    <circle cx="17" cy="17" r=${r} fill="none" stroke="var(--border)" stroke-width="3"/>
    <circle cx="17" cy="17" r=${r} fill="none" stroke=${color} stroke-width="3" stroke-dasharray=${c} stroke-dashoffset=${off} transform="rotate(-90 17 17)" stroke-linecap="round"/>
    <text x="17" y="21" text-anchor="middle" font-size="10" fill="var(--text-muted)">${complete}/${total}</text></svg></span>`;
}

function layout(domains, edges) {
  const ids = new Set(domains.map(d => d.slug));
  const ge = (edges || []).filter(e => ids.has(e.source) && ids.has(e.target));
  // Measure real card heights offscreen — dagre needs pixel dims; node x,y comes back as CENTER.
  const heights = {};
  const meas = document.createElement('div');
  meas.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;width:' + CARD_W + 'px';
  document.body.appendChild(meas);
  domains.forEach(d => {
    const el = document.createElement('div'); el.className = 'im-card'; el.style.width = CARD_W + 'px';
    el.innerHTML = `<h3>${d.title}</h3><div class="dc-meta">◯ ${d.total} topics</div>`;
    meas.appendChild(el); heights[d.slug] = el.offsetHeight || 96;
  });
  document.body.removeChild(meas);

  const g = new dagre.graphlib.Graph();
  // edgeLabelSpace:false — we draw no edge labels, so don't let dagre insert dummy label
  // nodes that inflate rank spacing.
  g.setGraph({ rankdir: 'TB', nodesep: PAD, ranksep: 60, marginx: 20, marginy: 20, edgeLabelSpace: false });
  g.setDefaultEdgeLabel(() => ({}));
  domains.forEach(d => g.setNode(d.slug, { width: CARD_W, height: heights[d.slug] }));
  // Structural parent edges weighted higher (shorter/straighter); leads_to stays light.
  ge.forEach(e => g.setEdge(e.source, e.target, e.type === 'parent' ? { weight: 3, minlen: 1 } : { weight: 1 }));
  dagre.layout(g);

  const pos = {};
  domains.forEach(d => { const n = g.node(d.slug); pos[d.slug] = { x: n.x - CARD_W / 2, y: n.y - heights[d.slug] / 2 }; });
  // g.edge(source, target) — NOT g.edge(e) (the spike bug: test the layout fn directly).
  const le = ge.map(e => ({ source: e.source, target: e.target, type: e.type, points: g.edge(e.source, e.target).points }));
  const gd = g.graph();
  return { pos, edges: le, width: gd.width, height: gd.height };
}

function pathD(points) {
  if (!points || points.length < 2) return '';
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const xc = (points[i].x + points[i + 1].x) / 2, yc = (points[i].y + points[i + 1].y) / 2;
    d += ` Q ${points[i].x} ${points[i].y} ${xc} ${yc}`;
  }
  const last = points[points.length - 1];
  d += ` L ${last.x} ${last.y}`;
  return d;
}

export function IteratedMapView({ domains, edges, islands }) {
  const islandSet = new Set(islands || []);
  const graphDomains = domains.filter(d => !islandSet.has(d.slug));
  const [L, setL] = useState(null);
  const [hover, setHover] = useState(null);
  const [view, setView] = useState({ k: 1, x: 0, y: 0 });
  const frameRef = useRef(null);

  useEffect(() => { if (graphDomains.length) setL(layout(graphDomains, edges)); }, []);

  // Fit-to-view: scale the computed canvas into the frame (single CSS transform).
  useEffect(() => {
    if (!L || !frameRef.current) return;
    const fw = frameRef.current.clientWidth, fh = frameRef.current.clientHeight;
    const k = Math.min(fw / L.width, fh / L.height, 1);
    setView({ k, x: (fw - L.width * k) / 2, y: 12 });
  }, [L]);

  if (!L) return html`<div class="loading">Computing layout…</div>`;
  const byslug = Object.fromEntries(domains.map(d => [d.slug, d]));
  const adj = {}; L.edges.forEach(e => { (adj[e.source] ||= new Set()).add(e.target); (adj[e.target] ||= new Set()).add(e.source); });
  const dim = s => hover && s !== hover && !(adj[hover] && adj[hover].has(s));
  const edgeActive = e => hover && (e.source === hover || e.target === hover);

  return html`<div class="iterated-map">
    <div class="im-legend">
      <span><svg width="34" height="10" aria-hidden="true"><line x1="2" y1="5" x2="32" y2="5" stroke="var(--text-muted)" stroke-width="2"/></svg> contains (sub-map)</span>
      <span><svg width="34" height="10" aria-hidden="true"><line x1="2" y1="5" x2="32" y2="5" stroke="var(--accent)" stroke-width="2" stroke-dasharray="5 3"/></svg> leads to</span>
    </div>
    <div class="im-frame" ref=${frameRef} style="height:520px;position:relative;overflow:hidden;border:1px solid var(--border);border-radius:12px">
      <div class="im-canvas" style="position:absolute;transform-origin:0 0;transform:translate(${view.x}px,${view.y}px) scale(${view.k});width:${L.width}px;height:${L.height}px">
        <svg class="im-edges" width=${L.width} height=${L.height} style="position:absolute;top:0;left:0;pointer-events:none">
          <defs>
            <marker id="im-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--text-muted)"/></marker>
            <marker id="im-arrow-lead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--accent)"/></marker>
          </defs>
          ${L.edges.map((e, i) => {
            const lead = e.type === 'leads_to';
            const active = edgeActive(e), faded = hover && !active;
            return html`<path key=${i} d=${pathD(e.points)} fill="none"
              stroke=${lead ? 'var(--accent)' : 'var(--text-muted)'} stroke-width=${active ? 2.5 : 1.5}
              stroke-dasharray=${lead ? '5 3' : '0'} opacity=${faded ? 0.15 : 1}
              marker-end=${lead ? 'url(#im-arrow-lead)' : 'url(#im-arrow)'} />`;
          })}
        </svg>
        ${graphDomains.map(d => html`
          <a key=${d.slug} class=${'im-card' + (d.depth > 0 ? ' is-child' : '')} href=${d.mapHref}
             data-domain=${d.slug}
             style="position:absolute;left:${L.pos[d.slug].x}px;top:${L.pos[d.slug].y}px;width:${CARD_W}px;opacity:${dim(d.slug) ? 0.25 : 1}"
             onMouseEnter=${() => setHover(d.slug)} onMouseLeave=${() => setHover(null)} onFocus=${() => setHover(d.slug)} onBlur=${() => setHover(null)}>
            <h3>${d.title}${d.depth > 0 && html`<span class="dc-sub-badge">sub-map</span>`}</h3>
            <div class="dc-meta"><${Ring} complete=${d.complete} total=${d.total} /> ${d.total} topics${d.inProgress ? `, ${d.inProgress} in progress` : ''}</div>
          </a>`)}
      </div>
    </div>
    ${islandSet.size > 0 && html`<div class="islands-panel"><h2>Standalone domains</h2><ul>
      ${[...islandSet].map(s => byslug[s]).filter(Boolean).map(d => html`<li><a href=${d.mapHref}>${d.title} (${d.complete}/${d.total})</a></li>`)}</ul></div>`}
  </div>`;
}
