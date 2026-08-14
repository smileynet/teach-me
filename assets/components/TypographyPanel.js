import { h, render } from 'preact';
import { useRef, useEffect } from 'preact/hooks';
import { useSignal } from '@preact/signals';
import htm from 'htm';
import { prefs, set, reset, DEFAULTS, FONT_FAMILY_MAP } from '../preferences.js';

const html = htm.bind(h);

const FONT_SIZES = [
  { label: 'S', value: '14px' },
  { label: 'M', value: '16px' },
  { label: 'L', value: '18px' },
  { label: 'XL', value: '20px' },
  { label: 'XXL', value: '22px' },
];

const FONT_FAMILIES = [
  { label: 'Serif', value: 'serif' },
  { label: 'Sans', value: 'sans' },
  { label: 'Dyslexic', value: 'dyslexic' },
];

const LINE_HEIGHTS = [
  { label: 'Compact', value: '1.5' },
  { label: 'Default', value: '1.7' },
  { label: 'Relaxed', value: '2.0' },
];

const WIDTHS = [
  { label: 'Narrow', value: '600px' },
  { label: 'Default', value: '740px' },
  { label: 'Wide', value: '900px' },
];

const SECTIONS = [
  { label: 'Expanded', value: false },
  { label: 'Collapsed', value: true },
];

const THEMES = [
  { label: 'Dark', value: 'dark' },
  { label: 'Light', value: 'light' },
  { label: 'Auto', value: 'auto' },
];

function TypographyPanel() {
  const open = useSignal(false);
  const panelRef = useRef(null);

  // Close on outside click or Escape
  useEffect(() => {
    if (!open.value) return;
    function handleClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) open.value = false;
    }
    function handleKey(e) { if (e.key === 'Escape') open.value = false; }
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKey);
    };
  }, [open.value]);

  function update(key, value) {
    set(key, value);
    if (key === 'sectionsCollapsed') {
      window.dispatchEvent(new CustomEvent('layout-change', { detail: { collapsed: value } }));
    }
  }

  function handleReset() {
    reset();
    window.dispatchEvent(new CustomEvent('layout-change', { detail: { collapsed: false } }));
  }

  const p = prefs.value;

  return html`
    <div class="typo-panel-container" ref=${panelRef}>
      <button
        class="typo-trigger"
        onClick=${() => { open.value = !open.value; }}
        aria-label="Reading preferences"
        aria-expanded=${open.value}
        title="Reading preferences"
      >Aa</button>

      ${open.value && html`
        <div class="typo-panel" role="dialog" aria-label="Reading preferences">
          <div class="typo-section">
            <label class="typo-label">Theme</label>
            <div class="typo-options">
              ${THEMES.map(t => html`
                <button
                  class="typo-opt ${p.theme === t.value ? 'active' : ''}"
                  onClick=${() => update('theme', t.value)}
                >${t.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Size</label>
            <div class="typo-options">
              ${FONT_SIZES.map(s => html`
                <button
                  class="typo-opt ${p.fontSize === s.value ? 'active' : ''}"
                  onClick=${() => update('fontSize', s.value)}
                >${s.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Font</label>
            <div class="typo-options">
              ${FONT_FAMILIES.map(f => html`
                <button
                  class="typo-opt ${p.fontFamily === f.value ? 'active' : ''}"
                  onClick=${() => update('fontFamily', f.value)}
                >${f.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Spacing</label>
            <div class="typo-options">
              ${LINE_HEIGHTS.map(l => html`
                <button
                  class="typo-opt ${p.lineHeight === l.value ? 'active' : ''}"
                  onClick=${() => update('lineHeight', l.value)}
                >${l.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Width</label>
            <div class="typo-options">
              ${WIDTHS.map(w => html`
                <button
                  class="typo-opt ${p.maxWidth === w.value ? 'active' : ''}"
                  onClick=${() => update('maxWidth', w.value)}
                >${w.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Sections</label>
            <div class="typo-options">
              ${SECTIONS.map(s => html`
                <button
                  class="typo-opt ${p.sectionsCollapsed === s.value ? 'active' : ''}"
                  onClick=${() => update('sectionsCollapsed', s.value)}
                >${s.label}</button>
              `)}
            </div>
          </div>

          <button class="typo-reset" onClick=${handleReset}>Reset to defaults</button>
        </div>
      `}
    </div>
  `;
}

export function mountTypographyPanel() {
  let target = document.getElementById('typo-panel');
  if (!target) {
    target = document.createElement('div');
    target.id = 'typo-panel';
    document.body.appendChild(target);
  }
  render(html`<${TypographyPanel} />`, target);
}

export { TypographyPanel };
