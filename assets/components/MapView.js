import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import htm from 'htm';
import { initTopicStates } from './store.js';
import { TopicCard } from './TopicCard.js';
import { EdgeLayer } from './EdgeLayer.js';

const html = htm.bind(h);

const CARD_WIDTH = 420;
const CARD_PAD = 60;

function computeLayout(topics) {
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

  // dagre layout
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'TB', nodesep: CARD_PAD, ranksep: 60, marginx: 24, marginy: 24 });
  g.setDefaultEdgeLabel(() => ({}));

  topics.forEach(t => {
    g.setNode(t.id, { width: CARD_WIDTH, height: measurements[t.id] || 200 });
  });
  topics.forEach(t => {
    t.prereqs.forEach(p => g.setEdge(p, t.id));
  });

  dagre.layout(g);

  const positions = {};
  topics.forEach(t => {
    const node = g.node(t.id);
    positions[t.id] = { x: node.x - CARD_WIDTH / 2, y: node.y - (measurements[t.id] || 200) / 2 };
  });

  const edges = [];
  g.edges().forEach(e => {
    edges.push(g.edge(e).points);
  });

  const graphData = g.graph();
  return { positions, edges, width: graphData.width, height: graphData.height };
}

export function MapView({ topics, leadsTo }) {
  const [layout, setLayout] = useState(null);

  useEffect(() => {
    if (!topics || !topics.length) return;
    initTopicStates(topics);
    const result = computeLayout(topics);
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
