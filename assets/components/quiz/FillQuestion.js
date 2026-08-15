import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

/**
 * FillQuestion — fill in blanks within a text template.
 */
export function FillQuestion({ question, index, total, onComplete }) {
  const parts = question.template.split(/___/);
  const blankCount = parts.length - 1;
  const [inputs, setInputs] = useState(Array(blankCount).fill(''));
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState([]);
  const [result, setResult] = useState(null);

  function updateInput(idx, value) {
    const arr = [...inputs];
    arr[idx] = value;
    setInputs(arr);
  }

  function normalize(s) {
    return s.toLowerCase().trim().replace(/[^a-z0-9 ]/g, '');
  }

  function checkAnswer() {
    const checks = inputs.map((input, idx) => {
      const expected = question.answers[idx];
      if (!expected) return false;
      return normalize(input) === normalize(expected);
    });
    setResults(checks);
    setSubmitted(true);

    const correctCount = checks.filter(Boolean).length;
    if (correctCount === blankCount) {
      setResult('got-it');
    } else if (correctCount >= blankCount * 0.5) {
      setResult('partial');
    } else {
      setResult('miss');
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && allFilled && !submitted) checkAnswer();
  }

  const allFilled = inputs.every(v => v.trim().length > 0);

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <div class="fill-template" aria-label="Fill in the blanks">
        ${parts.map((part, idx) => html`
          <span key=${idx}><span class="fill-part">${part}</span>${idx < blankCount && html`
            <input
              type="text"
              class="fill-blank ${submitted ? (results[idx] ? 'correct' : 'incorrect') : ''}"
              value=${inputs[idx]}
              onInput=${(e) => updateInput(idx, e.target.value)}
              onKeyDown=${handleKeyDown}
              disabled=${submitted}
              placeholder="..."
              aria-label="Blank ${idx + 1} of ${blankCount}"
              autocomplete="off"
              spellcheck="false"
            />`}</span>
        `)}
      </div>
      ${!submitted && html`
        <button class="btn primary" onClick=${checkAnswer} disabled=${!allFilled}>Check Answers</button>
      `}
      ${submitted && html`
        <div class="fill-feedback" role="status" aria-live="polite">
          <p class="feedback-result ${result}">
            ${result === 'got-it' ? '✓ All correct!' : result === 'partial' ? '◐ Some correct' : '✗ Not quite'}
          </p>
          ${result !== 'got-it' && html`
            <details class="correct-answer" open>
              <summary>Correct answers</summary>
              <ol class="correct-list">
                ${question.answers.map((a, i) => html`
                  <li class="${results[i] ? 'correct' : 'incorrect'}">
                    ${results[i] ? '✓' : '✗'} ${a}
                    ${!results[i] && inputs[i] ? html` <span class="your-answer">(you wrote: "${inputs[i]}")</span>` : ''}
                  </li>
                `)}
              </ol>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
