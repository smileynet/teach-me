import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

const currentIndex = signal(0);
const revealed = signal(false);
const scores = signal([]);

function QuizCard({ question, index, total }) {
  return html`
    <div class="quiz-card">
      <div class="quiz-progress">${index + 1} / ${total}</div>
      <p class="quiz-prompt">${question.prompt}</p>
      ${!revealed.value && html`
        <button class="btn primary" onClick=${() => { revealed.value = true; }}>Show Answer</button>
      `}
      ${revealed.value && html`
        <div class="quiz-answer">
          <p>${question.criteria || question.expected_answer || ''}</p>
          <div class="quiz-self-assess">
            <p class="assess-label">How well did you answer?</p>
            <div class="assess-buttons">
              <button class="btn" onClick=${() => next('miss')}>Missed it</button>
              <button class="btn" onClick=${() => next('partial')}>Partial</button>
              <button class="btn primary" onClick=${() => next('got-it')}>Got it</button>
            </div>
          </div>
        </div>
      `}
    </div>
  `;
}

function next(score) {
  scores.value = [...scores.value, score];
  revealed.value = false;
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

export function QuizView({ questions, title }) {
  if (!questions || !questions.length) {
    return html`<p class="empty">No questions available for this topic.</p>`;
  }

  if (currentIndex.value >= questions.length) {
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
      <${QuizCard}
        question=${questions[currentIndex.value]}
        index=${currentIndex.value}
        total=${questions.length}
      />
    </div>
  `;
}
