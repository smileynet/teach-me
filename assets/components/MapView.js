import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import htm from 'htm';
import { initTopicStates } from './store.js';
import { TopicCard } from './TopicCard.js';
import { EdgeLayer } from './EdgeLayer.js';

const html = htm.bind(h);

const CARD_WIDTH = 420;
const CARD_PAD = 60;

function computeLayout(topics, edges) {
  // Measure card heights by rendering offscreen
  const measurements = {};
  const measContainer = document.createElement('div');
  measContainer.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;width:' + CARD_WIDTH + 'px';
  document.body.appendChild(measContainer);

  topics.forEach(t => {
    const div = document.createElement('div');
    div.className = 'topic-card';
    div.style.width = CARD_WIDTH + 'px';
    div.innerHTML = `
      <h3>${t.title} <span class="badge">not started</span></h3>
      <p class="why">${t.why}</p>
      <p class="prereq-label">${t.prereqs.length ? 'After: ...' : 'Start here'}</p>
      <div class="actions"><button class="btn primary">Generate</button><button class="btn">Quiz</button><button class="btn">Subtopics</button></div>
    `;
    measContainer.appendChild(div);
    measurements[t.id] = div.offsetHeight;
  });
  document.body.removeChild(measContainer);

  const nodeIds = new Set(topics.map(t => t.id));
  // Prefer the explicit typed edge list (id-keyed). Fall back to per-topic prereqs
  // (also ids post-#257) so a map without an edges array still renders. The filter
  // guarantees both endpoints are real node ids → dagre never invents a phantom node.
  let graphEdges = (edges || []).filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
  if (graphEdges.length === 0) {
    graphEdges = [];
    topics.forEach(t => (t.prereqs || []).forEach(p => {
      if (nodeIds.has(p)) graphEdges.push({ source: p, target: t.id, type: 'prereq' });
    }));
  }

  // dagre layout
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'TB', nodesep: CARD_PAD, ranksep: 60, marginx: 24, marginy: 24 });
  g.setDefaultEdgeLabel(() => ({}));

  topics.forEach(t => {
    g.setNode(t.id, { width: CARD_WIDTH, height: measurements[t.id] || 200 });
  });
  graphEdges.forEach(e => g.setEdge(e.source, e.target, { type: e.type }));

  dagre.layout(g);

  const positions = {};
  topics.forEach(t => {
    const node = g.node(t.id);
    positions[t.id] = { x: node.x - CARD_WIDTH / 2, y: node.y - (measurements[t.id] || 200) / 2 };
  });

  const laidEdges = [];
  g.edges().forEach(e => {
    laidEdges.push({ points: g.edge(e).points, type: g.edge(e).type || 'prereq' });
  });

  const graphData = g.graph();
  return { positions, edges: laidEdges, width: graphData.width, height: graphData.height };
}

export function MapView({ topics, leadsTo, edges }) {
  const [layout, setLayout] = useState(null);

  useEffect(() => {
    if (!topics || !topics.length) return;
    initTopicStates(topics);
    const result = computeLayout(topics, edges);
    setLayout(result);
  }, []);

  if (!layout) return html`<div class="loading">Computing layout...</div>`;

  return html`
    <div class="dag-container">
      <div class="dag-canvas" style="width:${layout.width}px;height:${layout.height}px;position:relative">
        <${EdgeLayer} edges=${layout.edges} width=${layout.width} height=${layout.height} />
        ${topics.map(t => html`
          <${TopicCard}
            key=${t.id}
            topic=${t}
            allTopics=${topics}
            position=${layout.positions[t.id]}
          />
        `)}
      </div>
    </div>

    ${leadsTo && leadsTo.length > 0 && html`
      <div class="leads-to">
        <h2>Related Topics</h2>
        <div class="leads-to-grid">
          ${leadsTo.map(lt => html`
            <button class="leads-to-btn" data-domain=${lt.slug}>
              ${lt.slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              ${lt.why && html`<span class="leads-to-desc">${lt.why}</span>`}
            </button>
          `)}
        </div>
      </div>
    `}
  `;
}
