import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * FillQuestion — fill in blanks within a text template.
 *
 * Props:
 *   question.prompt — instruction text
 *   question.template — text with ___ placeholders for blanks
 *   question.answers — array of correct answers (one per blank, in order)
 *   onComplete(score) — called with 'got-it' | 'partial' | 'miss'
 */
export function FillQuestion({ question, index, total, onComplete }) {
  const parts = question.template.split(/___/);
  const blankCount = parts.length - 1;
  const inputs = signal(Array(blankCount).fill(''));
  const submitted = signal(false);
  const results = signal([]);
  const result = signal(null);

  function updateInput(idx, value) {
    const arr = [...inputs.value];
    arr[idx] = value;
    inputs.value = arr;
  }

  function normalize(s) {
    return s.toLowerCase().trim().replace(/[^a-z0-9 ]/g, '');
  }

  function checkAnswer() {
    const correct = question.answers;
    const checks = inputs.value.map((input, idx) => {
      const expected = correct[idx];
      if (!expected) return false;
      // Accept case-insensitive match, ignore punctuation
      return normalize(input) === normalize(expected);
    });
    results.value = checks;
    submitted.value = true;

    const correctCount = checks.filter(Boolean).length;
    if (correctCount === blankCount) {
      result.value = 'got-it';
    } else if (correctCount >= blankCount * 0.5) {
      result.value = 'partial';
    } else {
      result.value = 'miss';
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      const allFilled = inputs.value.every(v => v.trim().length > 0);
      if (allFilled && !submitted.value) checkAnswer();
    }
  }

  const allFilled = inputs.value.every(v => v.trim().length > 0);

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <div class="fill-template" aria-label="Fill in the blanks">
        ${parts.map((part, idx) => html`
          <span class="fill-part">${part}</span>${idx < blankCount && html`
            <input
              type="text"
              class="fill-blank ${submitted.value ? (results.value[idx] ? 'correct' : 'incorrect') : ''}"
              value=${inputs.value[idx]}
              onInput=${(e) => updateInput(idx, e.target.value)}
              onKeyDown=${handleKeyDown}
              disabled=${submitted.value}
              placeholder="..."
              aria-label="Blank ${idx + 1} of ${blankCount}"
              autocomplete="off"
              spellcheck="false"
            />`}
        `)}
      </div>
      ${!submitted.value && html`
        <button class="btn primary" onClick=${checkAnswer} disabled=${!allFilled}>Check Answers</button>
      `}
      ${submitted.value && html`
        <div class="fill-feedback">
          <p class="feedback-result ${result.value}">
            ${result.value === 'got-it' ? '✓ All correct!' : result.value === 'partial' ? '◐ Some correct' : '✗ Not quite'}
          </p>
          ${result.value !== 'got-it' && html`
            <details class="correct-answer" open>
              <summary>Correct answers</summary>
              <ol class="correct-list">
                ${question.answers.map((a, i) => html`
                  <li class="${results.value[i] ? 'correct' : 'incorrect'}">
                    ${results.value[i] ? '✓' : '✗'} ${a}
                    ${!results.value[i] && inputs.value[i] ? html` <span class="your-answer">(you wrote: "${inputs.value[i]}")</span>` : ''}
                  </li>
                `)}
              </ol>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result.value)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
