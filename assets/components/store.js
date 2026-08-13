import { signal, batch } from '@preact/signals';

// --- Topic state store ---
// Each topic gets its own signals for independent reactivity.
// Call initTopicStates(topicData) once on page load.

const topicStates = {};

export function initTopicStates(topics) {
  topics.forEach(t => {
    topicStates[t.id] = {
      status: signal(t.status || 'not-started'),
      progress: signal('')
    };
  });
}

export function getTopicState(topicId) {
  return topicStates[topicId];
}

export function setTopicStatus(topicId, status) {
  const state = topicStates[topicId];
  if (state) state.status.value = status;
}

export function setTopicProgress(topicId, text) {
  const state = topicStates[topicId];
  if (state) state.progress.value = text;
}

export function batchUpdate(fn) {
  batch(fn);
}

// --- Theme ---
export const theme = signal(
  document.documentElement.getAttribute('data-theme') || 'dark'
);

export function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', theme.value);
}
