import { h, render } from 'preact';
import { useState, useEffect, useRef } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

const STORAGE_KEY = 'teach-me-typography';

const DEFAULTS = {
  fontSize: '16px',
  fontFamily: "'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, serif",
  lineHeight: '1.7',
  maxWidth: '740px',
  layout: 'flow',
};

const FONT_SIZES = [
  { label: 'S', value: '14px' },
  { label: 'M', value: '16px' },
  { label: 'L', value: '18px' },
  { label: 'XL', value: '20px' },
  { label: 'XXL', value: '22px' },
];

const FONT_FAMILIES = [
  { label: 'Serif', value: "'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, serif" },
  { label: 'Sans', value: "system-ui, -apple-system, 'Segoe UI', sans-serif" },
  { label: 'Dyslexic', value: "'OpenDyslexic', sans-serif" },
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

const LAYOUTS = [
  { label: 'Flow', value: 'flow' },
  { label: 'Sections', value: 'sections' },
];

function loadPrefs() {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(STORAGE_KEY)) };
  } catch { return { ...DEFAULTS }; }
}

function savePrefs(prefs) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch {}
}

function applyPrefs(prefs) {
  const s = document.documentElement.style;
  s.setProperty('--font-size-base', prefs.fontSize);
  s.setProperty('--font-family-body', prefs.fontFamily);
  s.setProperty('--line-height-body', prefs.lineHeight);
  s.setProperty('--max-width-content', prefs.maxWidth);
}

function TypographyPanel() {
  const [open, setOpen] = useState(false);
  const [prefs, setPrefs] = useState(loadPrefs);
  const panelRef = useRef(null);

  useEffect(() => { applyPrefs(prefs); savePrefs(prefs); }, [prefs]);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    function handleClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) setOpen(false);
    }
    function handleKey(e) { if (e.key === 'Escape') setOpen(false); }
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKey);
    };
  }, [open]);

  function update(key, value) {
    setPrefs(p => ({ ...p, [key]: value }));
    if (key === 'layout') {
      window.dispatchEvent(new CustomEvent('layout-change', { detail: { layout: value } }));
    }
  }

  function reset() {
    setPrefs({ ...DEFAULTS });
    window.dispatchEvent(new CustomEvent('layout-change', { detail: { layout: 'flow' } }));
  }

  return html`
    <div class="typo-panel-container" ref=${panelRef}>
      <button
        class="typo-trigger"
        onClick=${() => setOpen(!open)}
        aria-label="Typography settings"
        aria-expanded=${open}
        title="Typography settings"
      >Aa</button>

      ${open && html`
        <div class="typo-panel" role="dialog" aria-label="Typography preferences">
          <div class="typo-section">
            <label class="typo-label">Size</label>
            <div class="typo-options">
              ${FONT_SIZES.map(s => html`
                <button
                  class="typo-opt ${prefs.fontSize === s.value ? 'active' : ''}"
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
                  class="typo-opt ${prefs.fontFamily === f.value ? 'active' : ''}"
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
                  class="typo-opt ${prefs.lineHeight === l.value ? 'active' : ''}"
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
                  class="typo-opt ${prefs.maxWidth === w.value ? 'active' : ''}"
                  onClick=${() => update('maxWidth', w.value)}
                >${w.label}</button>
              `)}
            </div>
          </div>

          <div class="typo-section">
            <label class="typo-label">Layout</label>
            <div class="typo-options">
              ${LAYOUTS.map(l => html`
                <button
                  class="typo-opt ${prefs.layout === l.value ? 'active' : ''}"
                  onClick=${() => update('layout', l.value)}
                >${l.label}</button>
              `)}
            </div>
          </div>

          <button class="typo-reset" onClick=${reset}>Reset to defaults</button>
        </div>
      `}
    </div>
  `;
}

// Auto-mount
function mount() {
  let target = document.getElementById('typo-panel');
  if (!target) {
    target = document.createElement('div');
    target.id = 'typo-panel';
    document.body.appendChild(target);
  }
  render(html`<${TypographyPanel} />`, target);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mount);
} else {
  mount();
}

export { TypographyPanel };
