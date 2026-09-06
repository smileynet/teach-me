import { h } from 'preact';
import htm from 'htm';
import { getTopicState } from './store.js';
import { StatusBadge } from './StatusBadge.js';
import { GenButton } from './GenButton.js';

const html = htm.bind(h);

export function TopicCard({ topic, allTopics, position }) {
  const state = getTopicState(topic.id);
  if (!state) return null;

  const hasPrereqs = topic.prereqs.length > 0;
  // Recommended-prereq indicator (#255): informational only, NO gating.
  // "met" = the prereq node's overlay status is complete or in-progress. Data is
  // already client-side (every prereq is another node; its status signal is in the
  // store, keyed by the same ULID) — no fetch. Reactive: re-renders if a prereq
  // completes mid-session. Color is paired with glyph + word (color-not-alone).
  const prereqItems = topic.prereqs.map(p => {
    const parent = allTopics.find(t => t.id === p);
    const title = parent ? parent.title.split('(')[0].trim() : p;
    const st = getTopicState(p)?.status.value;
    const met = st === 'complete' || st === 'in-progress';
    return { title, met };
  });

  return html`
    <div class="topic-card" data-topic-id=${topic.id} style="left:${position.x}px; top:${position.y}px">
      <h3>
        ${topic.title}
        <${StatusBadge} status=${state.status} />
      </h3>
      <p class="why">${topic.why}</p>
      ${!hasPrereqs && html`<p class="prereq-label">Start here</p>`}
      ${hasPrereqs && html`
        <ul class="prereq-list" aria-label="Recommended prerequisites">
          ${prereqItems.map(it => html`
            <li class=${'prereq-item ' + (it.met ? 'met' : 'unmet')}>
              <span class="prereq-mark" aria-hidden="true">${it.met ? '✓' : '○'}</span>
              <span class="prereq-state">${it.met ? 'met' : 'not yet'}</span>
              <span class="prereq-name">${it.title}</span>
            </li>
          `)}
        </ul>
      `}
      <div class="actions">
        <${GenButton} topicId=${topic.id} topicTitle=${topic.title} topicSlug=${topic.slug} lessonPath=${topic.lessonPath} />
        <button class="btn">Generate quiz</button>
        <button class="btn">Explore subtopics</button>
      </div>
    </div>
  `;
}
