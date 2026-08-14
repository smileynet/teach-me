import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * MatchQuestion — connect terms to definitions by clicking pairs.
 *
 * Props:
 *   question.prompt — instruction text
 *   question.pairs — array of [term, definition] tuples
 *   onComplete(score) — called with 'got-it' | 'partial' | 'miss'
 */
export function MatchQuestion({ question, index, total, onComplete }) {
  // Shuffle definitions independently of terms
  const terms = question.pairs.map(([t]) => t);
  const shuffledDefs = signal(shuffleArray(question.pairs.map(([, d]) => d)));
  const matches = signal({}); // { termIndex: defIndex }
  const selectedTerm = signal(null);
  const submitted = signal(false);
  const result = signal(null);

  function shuffleArray(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function selectTerm(idx) {
    if (submitted.value) return;
    selectedTerm.value = idx;
  }

  function selectDef(idx) {
    if (submitted.value || selectedTerm.value === null) return;
    // Check if this def is already matched to another term — remove that match
    const current = { ...matches.value };
    for (const [k, v] of Object.entries(current)) {
      if (v === idx) delete current[k];
    }
    current[selectedTerm.value] = idx;
    matches.value = current;
    selectedTerm.value = null;
  }

  function removeMatch(termIdx) {
    if (submitted.value) return;
    const current = { ...matches.value };
    delete current[termIdx];
    matches.value = current;
  }

  function checkAnswer() {
    const correctDefs = question.pairs.map(([, d]) => d);
    let correctCount = 0;
    for (const [termIdx, defIdx] of Object.entries(matches.value)) {
      const correctDef = correctDefs[parseInt(termIdx)];
      if (shuffledDefs.value[defIdx] === correctDef) {
        correctCount++;
      }
    }
    const totalPairs = terms.length;
    submitted.value = true;
    if (correctCount === totalPairs) {
      result.value = 'got-it';
    } else if (correctCount >= totalPairs * 0.5) {
      result.value = 'partial';
    } else {
      result.value = 'miss';
    }
  }

  function isDefMatched(defIdx) {
    return Object.values(matches.value).includes(defIdx);
  }

  function getMatchForTerm(termIdx) {
    const defIdx = matches.value[termIdx];
    if (defIdx === undefined) return null;
    return shuffledDefs.value[defIdx];
  }

  function isCorrectMatch(termIdx) {
    const defIdx = matches.value[termIdx];
    if (defIdx === undefined) return null;
    const correctDef = question.pairs[termIdx][1];
    return shuffledDefs.value[defIdx] === correctDef;
  }

  const allMatched = Object.keys(matches.value).length === terms.length;

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <div class="match-container">
        <div class="match-column" role="list" aria-label="Terms">
          ${terms.map((term, idx) => html`
            <button
              class="match-item term ${selectedTerm.value === idx ? 'selected' : ''} ${matches.value[idx] !== undefined ? 'matched' : ''} ${submitted.value && matches.value[idx] !== undefined ? (isCorrectMatch(idx) ? 'correct' : 'incorrect') : ''}"
              onClick=${() => matches.value[idx] !== undefined && !submitted.value ? removeMatch(idx) : selectTerm(idx)}
              disabled=${submitted.value}
              role="listitem"
              aria-label="${term}${getMatchForTerm(idx) ? ' → ' + getMatchForTerm(idx) : ''}"
            >
              <span class="match-text">${term}</span>
              ${getMatchForTerm(idx) && html`<span class="match-indicator">→ ${getMatchForTerm(idx)}</span>`}
            </button>
          `)}
        </div>
        <div class="match-column" role="list" aria-label="Definitions">
          ${shuffledDefs.value.map((def, idx) => html`
            <button
              class="match-item def ${isDefMatched(idx) ? 'matched' : ''}"
              onClick=${() => selectDef(idx)}
              disabled=${submitted.value || selectedTerm.value === null}
              role="listitem"
            >
              ${def}
            </button>
          `)}
        </div>
      </div>
      ${!submitted.value && html`
        <button class="btn primary" onClick=${checkAnswer} disabled=${!allMatched}>
          ${allMatched ? 'Check Matches' : `Match all pairs (${Object.keys(matches.value).length}/${terms.length})`}
        </button>
      `}
      ${submitted.value && html`
        <div class="match-feedback">
          <p class="feedback-result ${result.value}">
            ${result.value === 'got-it' ? '✓ All matched correctly!' : result.value === 'partial' ? '◐ Some matches correct' : '✗ Most matches incorrect'}
          </p>
          ${result.value !== 'got-it' && html`
            <details class="correct-answer">
              <summary>Show correct matches</summary>
              <ul class="correct-list">
                ${question.pairs.map(([t, d]) => html`<li><strong>${t}</strong> → ${d}</li>`)}
              </ul>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result.value)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
