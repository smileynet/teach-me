// GraphView (#283) — one dagre renderer for BOTH the topic map (MapView) and the domain
// forest (IteratedMapView). The 5-stage layout core (measure → dagre → center→corner →
// edge-path → render) was duplicated across the two; unified here with all divergences
// INJECTED (composition), never branched on a "level" flag:
//
//   nodes          — [{...}] the node population (topics OR domains)
//   edges          — [{source, target, type, why?}] endpoints in nodeKey()'s value space
//   nodeKey        — (node) => string   (id for topics, slug for domains)
//   renderNode     — (node, position, ui) => vnode   (TopicCard | domain <a>) — INJECTED
//   viewport       — 'scroll' (topic thread) | 'fit' (domain forest fit-to-view)  [VALUE axis]
//   edgeStyles     — { [type]: {stroke, dashed, arrow} }   (data table, not code)
//   cardWidth      — node width fed to dagre + measurement
//   graphOpts      — dagre setGraph overrides (margins, edgeLabelSpace, ...)
//   hover          — bool: enable neighbor-highlight (domain forest) — opt-in, NOT level-keyed
//   canvasClass    — caller-owned canvas class (topic page CSS + check-maps oracle expect
//                    'dag-canvas'; the domain view expects 'im-canvas'). Default 'gv-canvas'.
//   edgeLayerClass — caller-owned SVG edge-layer class ('edge-layer' | 'im-edges').
//
// Edge INVARIANT: edge.source/target are values in the SAME space nodeKey() returns (a caller
// contract; both callers honor it). Endpoints outside the node set are dropped + warned.
// Solid edges emit stroke-dasharray="none" (NOT "0") — the check-maps oracle keys on 'none'.
//
// Measurement: render the REAL injected node offscreen (visibility:hidden, attached — NOT
// display:none/detached which measure 0) and read offsetHeight. "Measure what you'll show."
import { h, render as prender } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

// --- pure-ish core: measure -> dagre -> center->corner -> edge paths ------------------
function computeLayout(nodes, edges, { nodeKey, renderNode, cardWidth, graphOpts }) {
  // 1. Offscreen-measure the REAL node markup (visibility:hidden keeps layout box).
  const heights = {};
  const meas = document.createElement('div');
  meas.style.cssText = `position:absolute;visibility:hidden;left:-9999px;width:${cardWidth}px`;
  document.body.appendChild(meas);
  nodes.forEach(n => {
    const host = document.createElement('div');
    host.style.width = cardWidth + 'px';
    meas.appendChild(host);
    // render the injected node with a dummy position; we only want its height.
    prender(renderNode(n, { x: 0, y: 0 }, { measuring: true }), host);
    heights[nodeKey(n)] = host.firstElementChild ? host.firstElementChild.offsetHeight : 200;
  });
  document.body.removeChild(meas);

  // 2. Edge pre-filter to real node keys → dagre never invents a phantom node.
  const keys = new Set(nodes.map(nodeKey));
  const ge = (edges || []).filter(e => keys.has(e.source) && keys.has(e.target));
  if ((edges || []).length && ge.length < edges.length && typeof console !== 'undefined') {
    console.warn(`[GraphView] dropped ${edges.length - ge.length} edge(s) with endpoints outside the node set`);
  }

  // 3. dagre layout (TB). Structural 'parent' edges weighted straighter; others light.
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'TB', nodesep: 40, ranksep: 60, marginx: 20, marginy: 20, ...(graphOpts || {}) });
  g.setDefaultEdgeLabel(() => ({}));
  nodes.forEach(n => g.setNode(nodeKey(n), { width: cardWidth, height: heights[nodeKey(n)] || 200 }));
  ge.forEach(e => g.setEdge(e.source, e.target,
    e.type === 'parent' ? { weight: 3, minlen: 1, type: e.type } : { weight: 1, type: e.type }));
  dagre.layout(g);

  // 4. center -> corner.
  const pos = {};
  nodes.forEach(n => {
    const k = nodeKey(n), node = g.node(k);
    pos[k] = { x: node.x - cardWidth / 2, y: node.y - (heights[k] || 200) / 2 };
  });

  // 5. edge path extraction — standardized on g.edge(v,w) (NOT g.edge(e); the documented
  // MapView spike bug). Carry source/target/type for styling + instrumentation.
  const laid = ge.map(e => ({
    source: e.source, target: e.target, type: e.type,
    points: g.edge(e.source, e.target).points,
  }));
  const gd = g.graph();
  return { pos, edges: laid, width: gd.width, height: gd.height };
}

function pathD(points) {
  if (!points || points.length < 2) return '';
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const c = points[i], n = points[i + 1];
    d += ` Q ${c.x} ${c.y} ${(c.x + n.x) / 2} ${(c.y + n.y) / 2}`;
  }
  const last = points[points.length - 1];
  d += ` L ${last.x} ${last.y}`;
  return d;
}

const DEFAULT_EDGE_STYLE = { stroke: 'var(--text-muted)', dashed: false, arrow: true };

export function GraphView(props) {
  const {
    nodes, edges, nodeKey, renderNode,
    viewport = 'scroll', edgeStyles = {}, cardWidth = 420, graphOpts, hover: hoverEnabled = false,
    canvasClass = 'gv-canvas', edgeLayerClass = 'gv-edges',
  } = props;

  const [L, setL] = useState(null);
  const [hover, setHover] = useState(null);
  const [view, setView] = useState({ k: 1, x: 0, y: 0 });
  const frameRef = useRef(null);

  useEffect(() => {
    if (!nodes || !nodes.length) return;
    setL(computeLayout(nodes, edges, { nodeKey, renderNode, cardWidth, graphOpts }));
  }, []);

  // fit-to-view (viewport==='fit'): single CSS transform scaling the canvas into the frame.
  useEffect(() => {
    if (viewport !== 'fit' || !L || !frameRef.current) return;
    const fw = frameRef.current.clientWidth, fh = frameRef.current.clientHeight;
    const k = Math.min(fw / L.width, fh / L.height, 1);
    setView({ k, x: (fw - L.width * k) / 2, y: 12 });
  }, [L, viewport]);

  if (!L) return html`<div class="loading">Computing layout…</div>`;

  const styleFor = t => ({ ...DEFAULT_EDGE_STYLE, ...(edgeStyles[t] || {}) });
  const adj = {};
  if (hoverEnabled) L.edges.forEach(e => { (adj[e.source] ||= new Set()).add(e.target); (adj[e.target] ||= new Set()).add(e.source); });
  const dim = k => hoverEnabled && hover && k !== hover && !(adj[hover] && adj[hover].has(k));
  const edgeActive = e => hoverEnabled && hover && (e.source === hover || e.target === hover);
  const ui = { hoverEnabled, setHover, dim };

  const svg = html`<svg class=${edgeLayerClass} width=${L.width} height=${L.height} style="position:absolute;top:0;left:0;pointer-events:none">
    <defs>
      <marker id="gv-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--text-muted)"/></marker>
    </defs>
    ${L.edges.map((e, i) => {
      const s = styleFor(e.type), active = edgeActive(e), faded = hoverEnabled && hover && !active;
      return html`<path key=${i} d=${pathD(e.points)} fill="none"
        stroke=${s.stroke} stroke-width=${active ? 2.5 : 1.5}
        stroke-dasharray=${s.dashed ? '5 3' : 'none'} opacity=${faded ? 0.15 : 1}
        marker-end=${s.arrow ? 'url(#gv-arrow)' : 'none'}
        data-source=${e.source} data-target=${e.target} data-type=${e.type} />`;
    })}
  </svg>`;

  const cards = nodes.map(n => {
    const k = nodeKey(n);
    return renderNode(n, L.pos[k], { ...ui, dimmed: dim(k), key: k });
  });

  const canvas = html`<div class=${canvasClass} style=${
    viewport === 'fit'
      ? `position:absolute;transform-origin:0 0;transform:translate(${view.x}px,${view.y}px) scale(${view.k});width:${L.width}px;height:${L.height}px`
      : `position:relative;width:${L.width}px;height:${L.height}px`
  } data-render-complete="true" data-edge-count=${L.edges.length}>${svg}${cards}</div>`;

  if (viewport === 'fit') {
    return html`<div class="gv-frame" ref=${frameRef} style="height:520px;position:relative;overflow:hidden;border:1px solid var(--border);border-radius:12px">${canvas}</div>`;
  }
  return html`<div class="gv-container" style="position:relative;width:100%;overflow-x:auto">${canvas}</div>`;
}
