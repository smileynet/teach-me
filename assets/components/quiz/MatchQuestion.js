import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

/**
 * MatchQuestion — connect terms to definitions by clicking pairs.
 */
export function MatchQuestion({ question, index, total, onComplete }) {
  const terms = question.pairs.map(([t]) => t);
  const correctDefs = question.pairs.map(([, d]) => d);

  function initDefs() {
    const arr = [...correctDefs];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  const [shuffledDefs] = useState(initDefs);
  const [matches, setMatches] = useState({}); // { termIndex: defIndex }
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);

  function selectTerm(idx) {
    if (submitted) return;
    if (matches[idx] !== undefined) {
      // Click matched term to unmatch
      const next = { ...matches };
      delete next[idx];
      setMatches(next);
      return;
    }
    setSelectedTerm(idx);
  }

  function selectDef(idx) {
    if (submitted || selectedTerm === null) return;
    // Remove any existing match to this def
    const next = { ...matches };
    for (const [k, v] of Object.entries(next)) {
      if (v === idx) delete next[k];
    }
    next[selectedTerm] = idx;
    setMatches(next);
    setSelectedTerm(null);
  }

  function checkAnswer() {
    let correctCount = 0;
    for (const [termIdx, defIdx] of Object.entries(matches)) {
      if (shuffledDefs[defIdx] === correctDefs[parseInt(termIdx)]) {
        correctCount++;
      }
    }
    setSubmitted(true);
    if (correctCount === terms.length) {
      setResult('got-it');
    } else if (correctCount >= terms.length * 0.5) {
      setResult('partial');
    } else {
      setResult('miss');
    }
  }

  function isCorrect(termIdx) {
    const defIdx = matches[termIdx];
    if (defIdx === undefined) return null;
    return shuffledDefs[defIdx] === correctDefs[termIdx];
  }

  function getPairIndex(termIdx) {
    // Return the order this match was made (0-based) for color coding
    const entries = Object.entries(matches);
    for (let i = 0; i < entries.length; i++) {
      if (parseInt(entries[i][0]) === termIdx) return i;
    }
    return -1;
  }

  function getDefPairIndex(defIdx) {
    const entries = Object.entries(matches);
    for (let i = 0; i < entries.length; i++) {
      if (entries[i][1] === defIdx) return i;
    }
    return -1;
  }

  const PAIR_LABELS = ['A', 'B', 'C', 'D', 'E', 'F'];

  const allMatched = Object.keys(matches).length === terms.length;

  return html`
    <div class="quiz-card interactive-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      <p class="match-hint">Click a term, then click its matching definition.</p>
      <div class="match-container">
        <div class="match-column" role="list" aria-label="Terms">
          ${terms.map((term, idx) => {
            const pairIdx = getPairIndex(idx);
            return html`
              <button
                key=${'t' + idx}
                class="match-item term ${selectedTerm === idx ? 'selected' : ''} ${matches[idx] !== undefined ? 'matched pair-' + pairIdx : ''} ${submitted && matches[idx] !== undefined ? (isCorrect(idx) ? 'correct' : 'incorrect') : ''}"
                onClick=${() => selectTerm(idx)}
                disabled=${submitted}
              >
                ${term}${pairIdx >= 0 && !submitted ? html`<span class="pair-label">${PAIR_LABELS[pairIdx]}</span>` : ''}
              </button>
            `;
          })}
        </div>
        <div class="match-column" role="list" aria-label="Definitions">
          ${shuffledDefs.map((def, idx) => {
            const pairIdx = getDefPairIndex(idx);
            return html`
              <button
                key=${'d' + idx}
                class="match-item def ${pairIdx >= 0 ? 'matched pair-' + pairIdx : ''} ${selectedTerm !== null ? 'selectable' : ''}"
                onClick=${() => selectDef(idx)}
                disabled=${submitted || selectedTerm === null}
              >
                ${def}${pairIdx >= 0 && !submitted ? html`<span class="pair-label">${PAIR_LABELS[pairIdx]}</span>` : ''}
              </button>
            `;
          })}
        </div>
      </div>
      ${!submitted && html`
        <button class="btn primary" onClick=${checkAnswer} disabled=${!allMatched}>
          ${allMatched ? 'Check Matches' : 'Match all pairs (' + Object.keys(matches).length + '/' + terms.length + ')'}
        </button>
      `}
      ${submitted && html`
        <div class="match-feedback" role="status" aria-live="polite">
          <p class="feedback-result ${result}">
            ${result === 'got-it' ? '✓ All matched correctly!' : result === 'partial' ? '◐ Some correct' : '✗ Most incorrect'}
          </p>
          ${result !== 'got-it' && html`
            <details class="correct-answer">
              <summary>Show correct matches</summary>
              <ul class="correct-list">
                ${question.pairs.map(([t, d]) => html`<li><strong>${t}</strong> → ${d}</li>`)}
              </ul>
            </details>
          `}
          <button class="btn primary" onClick=${() => onComplete(result)}>Continue</button>
        </div>
      `}
    </div>
  `;
}
