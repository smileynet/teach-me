import { h } from 'preact';
import htm from 'htm';
import { getTopicState } from './store.js';
import { StatusBadge } from './StatusBadge.js';
import { GenButton } from './GenButton.js';

const html = htm.bind(h);

export function TopicCard({ topic, allTopics, position }) {
  const state = getTopicState(topic.id);
  if (!state) return null;

  const prereqText = topic.prereqs.length === 0
    ? 'Start here'
    : 'After: ' + topic.prereqs.map(p => {
        const parent = allTopics.find(t => t.id === p);
        return parent ? parent.title.split('(')[0].trim() : p;
      }).join(', ');

  return html`
    <div class="topic-card" style="left:${position.x}px; top:${position.y}px">
      <h3>
        ${topic.title}
        <${StatusBadge} status=${state.status} />
      </h3>
      <p class="why">${topic.why}</p>
      <p class="prereq-label">${prereqText}</p>
      <div class="actions">
        <${GenButton} topicId=${topic.id} topicTitle=${topic.title} lessonPath=${topic.lessonPath} />
        <button class="btn">Generate quiz</button>
        <button class="btn">Explore subtopics</button>
      </div>
      ${state.status.value === 'generating' && html`
        <p class="gen-progress">${state.progress}</p>
      `}
    </div>
  `;
}
