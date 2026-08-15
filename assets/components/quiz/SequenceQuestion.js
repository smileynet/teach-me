import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

/**
 * SequenceQuestion — drag/click to reorder items into correct sequence.
 */
export function SequenceQuestion({ question, index, total, onComplete }) {
  const correct = question.correct_order || question.items.map((_, i) => i);

  function initItems() {
    const arr = question.items.map((text, i) => ({ text, id: i }));
    // Shuffle
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    // Avoid starting in correct order
    if (arr.every((item, idx) => item.id === correct[idx])) {
      [arr[0], arr[1]] = [arr[1], arr[0]];
    }
    return arr;
  }

  const [items, setItems] = useState(initItems);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(null);

  function moveUp(idx) {
    if (idx === 0 || submitted) return;
    const arr = [...items];
    [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
    setItems(arr);
  }

  function moveDown(idx) {
    if (idx === items.length - 1 || submitted) return;
    const arr = [...items];
    [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]];
    setItems(arr);
  }

  function swap(idx) {
    if (submitted) return;
    if (selected === null) {
      setSelected(idx);
    } else {
      const arr = [...items];
      [arr[selected], arr[idx]] = [arr[idx], arr[selected]];
      setItems(arr);
      setSelected(null);
    }
  }

  function checkAnswer() {
    const userOrder = items.map(item => item.id);
    const correctCount = userOrder.filter((id, idx) => id === correct[idx]).length;

    setSubmitted(true);
    if (correctCount === correct.length) {
      setResult('got-it');
    } else if (correctCount >= correct.length * 0.5) {
      setResult('partial');
    } else {
      setResult('miss');
    }
  }

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <div class="sequence-items" role="list" aria-label="Reorder these items">
        ${items.map((item, idx) => html`
          <div
            key=${item.id}
            class="sequence-item ${selected === idx ? 'selected' : ''} ${submitted ? (item.id === correct[idx] ? 'correct' : 'incorrect') : ''}"
            role="listitem"
          >
            <span class="sequence-num">${idx + 1}</span>
            <span class="sequence-text">${item.text}</span>
            ${!submitted && html`
              <span class="sequence-controls">
                <button class="seq-btn" onClick=${() => moveUp(idx)} disabled=${idx === 0} aria-label="Move up">↑</button>
                <button class="seq-btn" onClick=${() => moveDown(idx)} disabled=${idx === items.length - 1} aria-label="Move down">↓</button>
                <button class="seq-btn swap" onClick=${() => swap(idx)} aria-label="Swap">⇄</button>
              </span>
            `}
          </div>
        `)}
      </div>
      ${!submitted && html`
        <button class="btn primary" onClick=${checkAnswer}>Check Order</button>
      `}
      ${submitted && html`
        <div class="sequence-feedback" role="status" aria-live="polite">
          <p class="feedback-result ${result}">
            ${result === 'got-it' ? '✓ Perfect order!' : result === 'partial' ? '◐ Partially correct' : '✗ Not quite'}
          </p>
          ${result !== 'got-it' && html`
            <details class="correct-answer">
              <summary>Show correct order</summary>
              <ol class="correct-list">
                ${correct.map(i => html`<li>${question.items[i]}</li>`)}
              </ol>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
