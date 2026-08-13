import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';
import { getTopicState, setTopicStatus, setTopicProgress } from './store.js';
import { createGenerationStream } from '../services/generation.js';
import { GenerationStream } from './GenerationStream.js';

const html = htm.bind(h);

export function GenButton({ topicId, topicTitle, lessonPath }) {
  const state = getTopicState(topicId);
  const [stream, setStream] = useState(null);

  if (!state) return null;

  function handleGenerate() {
    const s = createGenerationStream(`teach me about ${topicTitle}`);
    setStream(s);
    setTopicStatus(topicId, 'generating');
    setTopicProgress(topicId, 'Connecting...');

    // Subscribe to stream updates
    const checkStatus = setInterval(() => {
      if (s.status.value === 'streaming') {
        const lastLine = s.lines.value[s.lines.value.length - 1];
        if (lastLine?.text) setTopicProgress(topicId, lastLine.text);
      } else if (s.status.value === 'done') {
        clearInterval(checkStatus);
        setTopicStatus(topicId, 'complete');
        setTopicProgress(topicId, '');
        setTimeout(() => location.reload(), 1500);
      } else if (s.status.value === 'error') {
        clearInterval(checkStatus);
        setTopicStatus(topicId, 'not-started');
        setTopicProgress(topicId, s.error.value || 'Generation failed');
      }
    }, 200);

    s.start();
  }

  if (state.status.value === 'not-started') {
    return html`<button class="btn primary" onClick=${handleGenerate}>Generate this topic</button>`;
  }
  if (state.status.value === 'complete') {
    if (lessonPath) {
      return html`<a href=${lessonPath} class="btn primary">Open lesson →</a>`;
    }
    return html`<span class="btn done">✓ Complete</span>`;
  }
  return null;
}
