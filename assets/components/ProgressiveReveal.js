import { h } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * ProgressiveReveal — step-through diagram/content reveal.
 * 
 * Mount into a container that has children with data-step="N" attributes.
 * Shows elements up to the current step, hides the rest.
 * 
 * Usage (in lesson HTML):
 *   <div id="reveal-container">
 *     <div data-step="1">First thing</div>
 *     <div data-step="2">Second thing</div>
 *     <div data-step="3">Third thing</div>
 *   </div>
 *   <div id="reveal-controls"></div>
 *   <script type="module">
 *     import { mountReveal } from '../assets/components/ProgressiveReveal.js';
 *     mountReveal('reveal-container', 'reveal-controls');
 *   </script>
 */

export function mountReveal(containerId, controlsId) {
  const container = document.getElementById(containerId);
  const controlsMount = document.getElementById(controlsId);
  if (!container || !controlsMount) return;

  const steps = container.querySelectorAll('[data-step]');
  const totalSteps = steps.length;
  if (totalSteps === 0) return;

  const currentStep = signal(1);

  // Apply visibility
  function applyVisibility() {
    steps.forEach(el => {
      const step = parseInt(el.getAttribute('data-step'), 10);
      el.style.display = step <= currentStep.value ? '' : 'none';
    });
  }

  // Initial state
  applyVisibility();

  // Mount controls using Preact render
  import('preact').then(({ render: r }) => {
    function Controls() {
      return html`
        <div class="reveal-controls" aria-live="polite">
          <button class="btn" onClick=${() => { if (currentStep.value > 1) { currentStep.value--; applyVisibility(); } }}
            disabled=${currentStep.value <= 1}>← Previous</button>
          <span class="reveal-counter">${currentStep.value} / ${totalSteps}</span>
          <button class="btn primary" onClick=${() => { if (currentStep.value < totalSteps) { currentStep.value++; applyVisibility(); } }}
            disabled=${currentStep.value >= totalSteps}>Next →</button>
        </div>
      `;
    }
    r(html`<${Controls} />`, controlsMount);
  });
}
