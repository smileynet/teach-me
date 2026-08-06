/* Progressive reveal — step through SVG diagrams with data-step attributes */
(function() {
  document.querySelectorAll('[data-reveal]').forEach(container => {
    const svg = container.querySelector('svg');
    if (!svg) return;

    const steps = new Set();
    svg.querySelectorAll('[data-step]').forEach(el => steps.add(parseInt(el.dataset.step)));
    const maxStep = Math.max(...steps);
    let current = 1;

    // Hide all except step 1
    function updateVisibility() {
      svg.querySelectorAll('[data-step]').forEach(el => {
        const step = parseInt(el.dataset.step);
        el.style.opacity = step <= current ? '1' : '0';
        el.style.transition = 'opacity 0.4s ease';
        // Highlight just-revealed elements
        if (step === current && current > 1) {
          el.style.filter = 'brightness(1.1)';
          setTimeout(() => el.style.filter = '', 800);
        }
      });
      stepLabel.textContent = `Step ${current} of ${maxStep}`;
      prevBtn.disabled = current <= 1;
      nextBtn.disabled = current >= maxStep;
    }

    // Controls
    const controls = document.createElement('div');
    controls.className = 'reveal-controls';
    controls.innerHTML = `
      <button class="reveal-btn" data-prev>← Prev</button>
      <span class="reveal-step"></span>
      <button class="reveal-btn" data-next>Next →</button>
    `;
    container.appendChild(controls);

    const prevBtn = controls.querySelector('[data-prev]');
    const nextBtn = controls.querySelector('[data-next]');
    const stepLabel = controls.querySelector('.reveal-step');

    prevBtn.addEventListener('click', () => { if (current > 1) { current--; updateVisibility(); } });
    nextBtn.addEventListener('click', () => { if (current < maxStep) { current++; updateVisibility(); } });

    // Keyboard
    container.tabIndex = 0;
    container.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight' && current < maxStep) { current++; updateVisibility(); }
      if (e.key === 'ArrowLeft' && current > 1) { current--; updateVisibility(); }
    });

    updateVisibility();
  });
})();
