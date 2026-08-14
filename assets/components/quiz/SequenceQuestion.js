import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * SequenceQuestion — drag/click to reorder items into correct sequence.
 *
 * Props:
 *   question.prompt — instruction text
 *   question.items — array of strings (displayed in shuffled order)
 *   question.correct_order — array of indices representing correct order
 *   onComplete(score) — called with 'got-it' | 'partial' | 'miss'
 */
export function SequenceQuestion({ question, index, total, onComplete }) {
  const items = signal(shuffle([...question.items.map((text, i) => ({ text, id: i }))]));
  const submitted = signal(false);
  const result = signal(null);
  const selected = signal(null);

  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    // Avoid starting in correct order
    const correct = question.correct_order || question.items.map((_, i) => i);
    if (a.every((item, idx) => item.id === correct[idx])) {
      [a[0], a[1]] = [a[1], a[0]];
    }
    return a;
  }

  function moveUp(idx) {
    if (idx === 0 || submitted.value) return;
    const arr = [...items.value];
    [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
    items.value = arr;
  }

  function moveDown(idx) {
    if (idx === items.value.length - 1 || submitted.value) return;
    const arr = [...items.value];
    [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]];
    items.value = arr;
  }

  function swap(idx) {
    if (submitted.value) return;
    if (selected.value === null) {
      selected.value = idx;
    } else {
      const arr = [...items.value];
      [arr[selected.value], arr[idx]] = [arr[idx], arr[selected.value]];
      items.value = arr;
      selected.value = null;
    }
  }

  function checkAnswer() {
    const correct = question.correct_order || question.items.map((_, i) => i);
    const userOrder = items.value.map(item => item.id);
    const correctCount = userOrder.filter((id, idx) => id === correct[idx]).length;
    const total = correct.length;

    submitted.value = true;
    if (correctCount === total) {
      result.value = 'got-it';
    } else if (correctCount >= total * 0.5) {
      result.value = 'partial';
    } else {
      result.value = 'miss';
    }
  }

  function showCorrect() {
    const correct = question.correct_order || question.items.map((_, i) => i);
    return correct.map(i => question.items[i]);
  }

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <div class="sequence-items" role="list" aria-label="Reorder these items">
        ${items.value.map((item, idx) => html`
          <div
            class="sequence-item ${selected.value === idx ? 'selected' : ''} ${submitted.value ? (item.id === (question.correct_order || question.items.map((_, i) => i))[idx] ? 'correct' : 'incorrect') : ''}"
            role="listitem"
            aria-label="${item.text} (position ${idx + 1})"
          >
            <span class="sequence-num">${idx + 1}</span>
            <span class="sequence-text">${item.text}</span>
            ${!submitted.value && html`
              <span class="sequence-controls">
                <button class="seq-btn" onClick=${() => moveUp(idx)} disabled=${idx === 0} aria-label="Move up" title="Move up">↑</button>
                <button class="seq-btn" onClick=${() => moveDown(idx)} disabled=${idx === items.value.length - 1} aria-label="Move down" title="Move down">↓</button>
                <button class="seq-btn swap" onClick=${() => swap(idx)} aria-label="Select to swap" title="Click two items to swap">⇄</button>
              </span>
            `}
          </div>
        `)}
      </div>
      ${!submitted.value && html`
        <button class="btn primary" onClick=${checkAnswer}>Check Order</button>
      `}
      ${submitted.value && html`
        <div class="sequence-feedback">
          <p class="feedback-result ${result.value}">
            ${result.value === 'got-it' ? '✓ Perfect order!' : result.value === 'partial' ? '◐ Partially correct' : '✗ Not quite'}
          </p>
          ${result.value !== 'got-it' && html`
            <details class="correct-answer">
              <summary>Show correct order</summary>
              <ol class="correct-list">
                ${showCorrect().map(text => html`<li>${text}</li>`)}
              </ol>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result.value)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
