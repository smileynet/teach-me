// MapView (#283) — the topic map: delegates layout to the unified GraphView, injecting the
// stateful TopicCard as renderNode. Topic-level config: nodeKey=id, viewport='scroll', prereq
// synthesis upstream of the layout core, leadsTo grid as caller-side chrome.
import { h } from 'preact';
import htm from 'htm';
import { initTopicStates } from './store.js';
import { TopicCard } from './TopicCard.js';
import { GraphView } from './GraphView.js';

const html = htm.bind(h);

// Topic edge styling: prereq/leads_to solid + arrow; related dashed, no arrow (signaling —
// symmetric adjacency). GraphView emits dasharray="none" for solid (oracle contract).
const TOPIC_EDGE_STYLES = {
  prereq: { stroke: 'var(--border)', dashed: false, arrow: true },
  leads_to: { stroke: 'var(--border)', dashed: false, arrow: true },
  related: { stroke: 'var(--border)', dashed: true, arrow: false },
};

export function MapView({ topics, leadsTo, edges }) {
  if (topics && topics.length) initTopicStates(topics);

  // Edge source: explicit typed list (id-keyed) if present, else synthesize from prereqs
  // UPSTREAM of GraphView (the core carries no fallback). Both are id-keyed.
  let graphEdges = edges && edges.length ? edges : [];
  if (!graphEdges.length && topics) {
    const ids = new Set(topics.map(t => t.id));
    graphEdges = [];
    topics.forEach(t => (t.prereqs || []).forEach(p => {
      if (ids.has(p)) graphEdges.push({ source: p, target: t.id, type: 'prereq' });
    }));
  }

  const renderNode = (topic, position) => html`
    <${TopicCard} key=${topic.id} topic=${topic} allTopics=${topics} position=${position} />`;

  return html`
    <${GraphView}
      nodes=${topics}
      edges=${graphEdges}
      nodeKey=${t => t.id}
      renderNode=${renderNode}
      viewport="scroll"
      edgeStyles=${TOPIC_EDGE_STYLES}
      cardWidth=${420}
      graphOpts=${{ nodesep: 60, marginx: 24, marginy: 24 }}
      canvasClass="dag-canvas"
      edgeLayerClass="edge-layer"
    />

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
