/* Quiz component — shuffles answers at render, immediate feedback */
(function() {
  document.querySelectorAll('[data-quiz]').forEach(quiz => {
    const questions = quiz.querySelectorAll('.quiz-question');
    let score = 0, total = questions.length, answered = 0;

    questions.forEach(q => {
      const correctIdx = parseInt(q.dataset.correct) - 1;
      const options = Array.from(q.querySelectorAll('.quiz-option'));
      const correct = options[correctIdx];

      // Fisher-Yates shuffle
      for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
      }

      // Re-insert shuffled
      const container = document.createElement('fieldset');
      container.className = 'quiz-options';
      container.setAttribute('role', 'radiogroup');
      const legend = q.querySelector('.quiz-prompt');
      if (legend) container.appendChild(legend);

      options.forEach((opt, i) => {
        const label = document.createElement('label');
        label.className = 'quiz-label';
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = `q-${Math.random().toString(36).slice(2, 8)}`;
        input.className = 'quiz-radio';
        label.appendChild(input);
        label.appendChild(document.createTextNode(' ' + opt.textContent));
        label.dataset.explanation = opt.dataset.explanation || '';
        // Sources as JSON array: [{url, label, section}]
        label.dataset.sources = opt.dataset.sources || '[]';
        label.dataset.isCorrect = opt === correct ? 'true' : 'false';
        container.appendChild(label);
        opt.remove();
      });

      q.innerHTML = '';
      q.appendChild(container);

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

        // Show explanation with source links
        const explanation = document.createElement('div');
        explanation.className = 'quiz-explanation';
        explanation.innerHTML = selected.dataset.explanation;
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
        container.appendChild(explanation);

        // Disable further input
        container.querySelectorAll('input').forEach(inp => inp.disabled = true);

        // Show score if all answered
        if (answered === total) {
          const summary = document.createElement('div');
          summary.className = 'quiz-summary';
          summary.innerHTML = `<strong>Score: ${score}/${total}</strong> — ${
            score === total ? '🎯 Perfect!' :
            score >= total * 0.7 ? '👍 Good understanding.' :
            '📖 Review the material and try again.'
          }`;
          quiz.appendChild(summary);
        }
      });
    });
  });
})();
