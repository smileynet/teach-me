import { h } from 'preact';
import { useState } from 'preact/hooks';
import { signal } from '@preact/signals';
import htm from 'htm';
import { SequenceQuestion } from './quiz/SequenceQuestion.js';
import { MatchQuestion } from './quiz/MatchQuestion.js';
import { FillQuestion } from './quiz/FillQuestion.js';

const html = htm.bind(h);

const currentIndex = signal(0);
const scores = signal([]);
const showAll = signal(false);

/**
 * AnswerCriteria — formats criteria text into a readable checklist,
 * plus "Another angle" companion explanation if available.
 */
function AnswerCriteria({ text, anotherAngle }) {
  if (!text) return null;

  // Extract bonus section if present
  const bonusMatch = text.match(/\b[Bb]onus:?\s*(.+?)$/);
  const bonus = bonusMatch ? bonusMatch[1].trim() : null;
  const mainText = bonus ? text.slice(0, bonusMatch.index).trim() : text;

  // Extract numbered points: (1) ..., (2) ..., etc.
  const pointsMatch = mainText.match(/\(\d+\)\s*[^(]+/g);

  const criteriaBlock = pointsMatch && pointsMatch.length > 1
    ? html`
        <div class="answer-criteria">
          <p class="criteria-heading">Key points to check your answer against:</p>
          <ol class="criteria-list">
            ${pointsMatch.map(p => html`<li>${p.replace(/^\(\d+\)\s*/, '').replace(/[,;]\s*$/, '').trim()}</li>`)}
          </ol>
          ${bonus && html`<p class="criteria-bonus"><strong>Bonus:</strong> ${bonus}</p>`}
        </div>
      `
    : html`
        <div class="answer-criteria">
          <p class="criteria-heading">Key points:</p>
          <p>${text}</p>
        </div>
      `;

  return html`
    ${criteriaBlock}
    ${anotherAngle && html`
      <div class="another-angle">
        <span class="another-angle-icon">💡</span>
        <div class="another-angle-content">
          <p class="another-angle-heading">Another angle</p>
          <p class="another-angle-text">${anotherAngle}</p>
        </div>
      </div>
    `}
  `;
}

function QuizCard({ question, index, total, onComplete }) {
  const [revealed, setRevealed] = useState(false);
  const [scored, setScored] = useState(false);

  function handleScore(score) {
    setScored(true);
    if (onComplete) onComplete(score);
  }

  return html`
    <div class="quiz-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      ${!revealed && html`
        <button class="btn primary" onClick=${() => setRevealed(true)}>Show Answer</button>
      `}
      ${revealed && html`
        <div class="quiz-answer" role="status" aria-live="polite">
          <${AnswerCriteria} text=${question.criteria || question.expected_answer || ''} anotherAngle=${question.eli5 || question.another_angle || null} />
          ${!scored && html`
            <div class="quiz-self-assess">
              <p class="assess-label">How well did you answer?</p>
              <div class="assess-buttons">
                <button class="btn" onClick=${() => handleScore('miss')}>Missed it</button>
                <button class="btn" onClick=${() => handleScore('partial')}>Partial</button>
                <button class="btn primary" onClick=${() => handleScore('got-it')}>Got it</button>
              </div>
            </div>
          `}
          ${scored && html`
            <p class="assess-done">✓ Recorded</p>
          `}
        </div>
      `}
    </div>
  `;
}

function next(score) {
  scores.value = [...scores.value, score];
  currentIndex.value++;
}

function QuizSummary({ questions }) {
  const total = questions.length;
  const got = scores.value.filter(s => s === 'got-it').length;
  const partial = scores.value.filter(s => s === 'partial').length;
  const missed = scores.value.filter(s => s === 'miss').length;

  return html`
    <div class="quiz-summary">
      <h2>Quiz Complete</h2>
      <div class="summary-stats">
        <span class="stat got">✓ ${got} got it</span>
        <span class="stat partial">◐ ${partial} partial</span>
        <span class="stat missed">✗ ${missed} missed</span>
      </div>
      <p class="summary-note">${got === total ? 'Perfect — you own this material.' : got >= total * 0.7 ? 'Solid understanding. Review the ones you missed.' : 'Worth revisiting the lesson before moving on.'}</p>
      <div class="summary-actions">
        <button class="btn" onClick=${() => { currentIndex.value = 0; scores.value = []; }}>Retry</button>
        <a href="javascript:history.back()" class="btn">← Back</a>
      </div>
    </div>
  `;
}

function interactiveNext(score) {
  scores.value = [...scores.value, score];
  currentIndex.value++;
}

function QuestionRouter({ question, index, total, onComplete }) {
  const type = question.type || 'open';
  const handler = onComplete || interactiveNext;

  switch (type) {
    case 'sequence':
      return html`<${SequenceQuestion} question=${question} index=${index} total=${total} onComplete=${handler} />`;
    case 'match':
      return html`<${MatchQuestion} question=${question} index=${index} total=${total} onComplete=${handler} />`;
    case 'fill':
      return html`<${FillQuestion} question=${question} index=${index} total=${total} onComplete=${handler} />`;
    default:
      return html`<${QuizCard} question=${question} index=${index} total=${total} onComplete=${handler} />`;
  }
}

export function QuizView({ questions, title }) {
  if (!questions || !questions.length) {
    return html`<p class="empty">No questions available for this topic.</p>`;
  }

  if (!showAll.value && currentIndex.value >= questions.length) {
    return html`
      <div class="quiz-view">
        <h1>${title || 'Quiz'}</h1>
        <${QuizSummary} questions=${questions} />
      </div>
    `;
  }

  return html`
    <div class="quiz-view">
      <h1>${title || 'Quiz'}</h1>
      <div class="quiz-mode-toggle">
        ${questions.length > 1 && html`
          <button class="mode-btn ${!showAll.value ? 'active' : ''}" onClick=${() => { showAll.value = false; }}>One at a time</button>
          <button class="mode-btn ${showAll.value ? 'active' : ''}" onClick=${() => { showAll.value = true; }}>Show all</button>
        `}
      </div>
      ${showAll.value ? html`
        <div class="quiz-all">
          ${questions.map((q, i) => html`
            <${QuestionRouter} question=${q} index=${i} total=${questions.length} key=${i} onComplete=${(score) => { scores.value = [...scores.value, score]; }} />
          `)}
        </div>
      ` : html`
        <${QuestionRouter}
          question=${questions[currentIndex.value]}
          index=${currentIndex.value}
          total=${questions.length}
        />
      `}
    </div>
  `;
}
