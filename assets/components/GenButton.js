import { h } from 'preact';
import htm from 'htm';
import { getTopicState, setTopicStatus, setTopicProgress } from './store.js';

const html = htm.bind(h);

export function GenButton({ topicId, topicTitle }) {
  const state = getTopicState(topicId);
  if (!state) return null;

  function handleGenerate() {
    setTopicStatus(topicId, 'generating');
    setTopicProgress(topicId, 'Connecting...');

    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: `teach me about ${topicTitle}`, mock: false })
    })
      .then(r => r.json())
      .then(data => {
        const es = new EventSource(data.stream_url);

        es.addEventListener('line', e => {
          const line = JSON.parse(e.data);
          if (line.text) setTopicProgress(topicId, line.text);
        });

        es.addEventListener('done', () => {
          es.close();
          setTopicStatus(topicId, 'complete');
          setTopicProgress(topicId, '');
        });

        es.addEventListener('error', () => {
          es.close();
          setTopicStatus(topicId, 'not-started');
          setTopicProgress(topicId, 'Generation failed — try again');
        });
      })
      .catch(() => {
        setTopicStatus(topicId, 'not-started');
        setTopicProgress(topicId, 'Could not connect to server');
      });
  }

  if (state.status.value === 'not-started') {
    return html`<button class="btn primary" onClick=${handleGenerate}>Generate this topic</button>`;
  }
  if (state.status.value === 'complete') {
    return html`<button class="btn primary">Open lesson →</button>`;
  }
  return null;
}
