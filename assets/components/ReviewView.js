import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

const currentIndex = signal(0);
const revealed = signal(false);
const ratings = signal([]);

function ReviewCard({ card, index, total }) {
  return html`
    <div class="review-card">
      <div class="review-progress">${index + 1} / ${total}</div>
      <p class="review-prompt">${card.prompt}</p>
      ${!revealed.value && html`
        <button class="btn primary" onClick=${() => { revealed.value = true; }}>Reveal Answer</button>
      `}
      ${revealed.value && html`
        <div class="review-answer">
          <p>${card.criteria || card.answer || ''}</p>
          <div class="quality-rating">
            <p class="rating-label">Rate your recall:</p>
            <div class="rating-buttons">
              <button class="btn rating-1" onClick=${() => rate(1)}>1 — Forgot</button>
              <button class="btn rating-3" onClick=${() => rate(3)}>3 — Hard</button>
              <button class="btn rating-4" onClick=${() => rate(4)}>4 — Good</button>
              <button class="btn primary rating-5" onClick=${() => rate(5)}>5 — Easy</button>
            </div>
          </div>
        </div>
      `}
    </div>
  `;
}

function rate(quality) {
  ratings.value = [...ratings.value, { index: currentIndex.value, quality }];
  revealed.value = false;
  currentIndex.value++;
}

function ReviewSummary({ cards }) {
  const total = cards.length;
  const easy = ratings.value.filter(r => r.quality >= 4).length;
  const hard = ratings.value.filter(r => r.quality === 3).length;
  const forgot = ratings.value.filter(r => r.quality <= 2).length;

  return html`
    <div class="review-summary">
      <h2>Review Complete</h2>
      <div class="summary-stats">
        <span class="stat easy">✓ ${easy} easy</span>
        <span class="stat hard">◐ ${hard} hard</span>
        <span class="stat forgot">✗ ${forgot} forgot</span>
      </div>
      <p class="summary-pct">${Math.round(easy / total * 100)}% retention</p>
      <div class="summary-actions">
        <button class="btn" onClick=${() => { currentIndex.value = 0; ratings.value = []; }}>Review again</button>
        <a href="javascript:history.back()" class="btn">← Back</a>
      </div>
    </div>
  `;
}

export function ReviewView({ cards, title }) {
  if (!cards || !cards.length) {
    return html`<p class="empty">No cards due for review.</p>`;
  }

  if (currentIndex.value >= cards.length) {
    return html`
      <div class="review-view">
        <h1>${title || 'Review'}</h1>
        <${ReviewSummary} cards=${cards} />
      </div>
    `;
  }

  return html`
    <div class="review-view">
      <h1>${title || 'Review'}</h1>
      <${ReviewCard}
        card=${cards[currentIndex.value]}
        index=${currentIndex.value}
        total=${cards.length}
      />
    </div>
  `;
}
