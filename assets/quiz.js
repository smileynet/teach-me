/* Quiz component — shuffles answers at render, immediate feedback, persists state */
(function() {
  document.querySelectorAll('[data-quiz]').forEach(quiz => {
    const quizId = quiz.dataset.quiz || quiz.id || 'quiz-' + Math.random().toString(36).slice(2, 8);
    const questions = quiz.querySelectorAll('.quiz-question');
    const total = questions.length;
    let score = 0, answered = 0;

    // Load persisted state
    const storageKey = 'teach-me-quiz-' + quizId;
    const saved = loadState(storageKey);

    questions.forEach((q, qIdx) => {
      const correctIdx = parseInt(q.dataset.correct) - 1;
      const options = Array.from(q.querySelectorAll('.quiz-option'));
      const correct = options[correctIdx];

      // Fisher-Yates shuffle
      for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
      }

      // Build fieldset
      const container = document.createElement('fieldset');
      container.className = 'quiz-options';
      container.setAttribute('role', 'radiogroup');
      const legend = q.querySelector('.quiz-prompt');
      if (legend) container.appendChild(legend);

      // Feedback region (aria-live for screen readers)
      const feedback = document.createElement('div');
      feedback.className = 'quiz-feedback-region';
      feedback.setAttribute('aria-live', 'polite');
      feedback.setAttribute('aria-atomic', 'true');

      const radioName = `q-${quizId}-${qIdx}`;

      options.forEach((opt) => {
        const label = document.createElement('label');
        label.className = 'quiz-label';
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = radioName;
        input.className = 'quiz-radio';
        label.appendChild(input);
        label.appendChild(document.createTextNode(' ' + opt.textContent));
        label.dataset.explanation = opt.dataset.explanation || '';
        label.dataset.sources = opt.dataset.sources || '[]';
        label.dataset.isCorrect = opt === correct ? 'true' : 'false';
        container.appendChild(label);
        opt.remove();
      });

      container.appendChild(feedback);
      q.innerHTML = '';
      q.appendChild(container);

      // Restore saved answer
      if (saved && saved[qIdx] !== undefined) {
        restoreAnswer(container, feedback, saved[qIdx], qIdx);
        answered++;
        if (saved[qIdx].correct) score++;
      }

      // Handle selection
      container.addEventListener('change', e => {
        if (q.dataset.answered) return;
        q.dataset.answered = 'true';
        answered++;
        const selected = e.target.closest('.quiz-label');
        const isCorrect = selected.dataset.isCorrect === 'true';

        if (isCorrect) {
          score++;
          selected.classList.add('quiz-correct');
        } else {
          selected.classList.add('quiz-incorrect');
          container.querySelectorAll('.quiz-label').forEach(l => {
            if (l.dataset.isCorrect === 'true') l.classList.add('quiz-correct');
          });
        }

        // Show explanation in aria-live region
        showFeedback(feedback, selected, isCorrect);

        // Disable further input
        container.querySelectorAll('input').forEach(inp => inp.disabled = true);

        // Persist
        saveAnswer(storageKey, qIdx, { correct: isCorrect, selectedText: selected.textContent.trim() });

        // Show score if all answered
        if (answered === total) showSummary(quiz, score, total);
      });
    });

    // Show summary if already complete from saved state
    if (saved && answered === total) showSummary(quiz, score, total);
  });

  function showFeedback(region, selected, isCorrect) {
    const explanation = document.createElement('div');
    explanation.className = 'quiz-explanation';
    const prefix = isCorrect ? '✓ Correct. ' : '✗ Incorrect. ';
    explanation.innerHTML = prefix + (selected.dataset.explanation || '');
    const sources = JSON.parse(selected.dataset.sources || '[]');
    if (sources.length) {
      const list = document.createElement('ul');
      list.className = 'quiz-sources';
      sources.forEach(src => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = src.url;
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = src.label;
        li.appendChild(link);
        if (src.section) {
          const detail = document.createElement('span');
          detail.className = 'quiz-source-detail';
          detail.textContent = ' — ' + src.section;
          li.appendChild(detail);
        }
        list.appendChild(li);
      });
      explanation.appendChild(list);
    }
    region.appendChild(explanation);
  }

  function showSummary(quiz, score, total) {
    if (quiz.querySelector('.quiz-summary')) return;
    const summary = document.createElement('div');
    summary.className = 'quiz-summary';
    summary.setAttribute('aria-live', 'polite');
    summary.innerHTML = '<strong>Score: ' + score + '/' + total + '</strong> — ' + (
      score === total ? '🎯 Perfect!' :
      score >= total * 0.7 ? '👍 Good understanding.' :
      '📖 Review the material and try again.'
    );
    quiz.appendChild(summary);
  }

  function loadState(key) {
    try { return JSON.parse(localStorage.getItem(key)); } catch (e) { return null; }
  }

  function saveAnswer(key, qIdx, data) {
    var state = loadState(key) || {};
    state[qIdx] = data;
    try { localStorage.setItem(key, JSON.stringify(state)); } catch (e) { /* quota */ }
  }

  function restoreAnswer(container, feedback, data, qIdx) {
    var labels = container.querySelectorAll('.quiz-label');
    labels.forEach(l => {
      if (l.dataset.isCorrect === 'true') l.classList.add('quiz-correct');
      if (l.textContent.trim() === data.selectedText && !data.correct) {
        l.classList.add('quiz-incorrect');
      }
    });
    container.querySelectorAll('input').forEach(inp => inp.disabled = true);
    container.closest('.quiz-question').dataset.answered = 'true';
    // Brief restored feedback
    var note = document.createElement('div');
    note.className = 'quiz-explanation';
    note.textContent = data.correct ? '✓ Correct (previously answered)' : '✗ Incorrect (previously answered)';
    feedback.appendChild(note);
  }
})();
