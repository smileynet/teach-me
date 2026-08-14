/**
 * preferences.js — THE single source of truth for all user preferences.
 *
 * Exports:
 *   prefs        — signal containing the full preferences object
 *   effectiveTheme — computed signal resolving 'auto' to actual theme
 *   set(key, val) — update one preference (auto-persists + auto-applies)
 *   reset()       — restore all defaults
 *
 * Persistence: single localStorage key 'teach-me-prefs-v1'
 * DOM application: effect() auto-applies CSS vars + data-theme on change
 * Migration: handles legacy keys (teach-me-typography, teach-me-theme)
 */

import { signal, effect, computed } from '@preact/signals';

const STORAGE_KEY = 'teach-me-prefs-v1';

const FONT_FAMILY_MAP = {
  serif: "'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, serif",
  sans: "system-ui, -apple-system, 'Segoe UI', sans-serif",
  dyslexic: "'OpenDyslexic', sans-serif",
};

export const DEFAULTS = {
  _v: 1,
  theme: 'auto',
  fontSize: '16px',
  fontFamily: 'serif',
  lineHeight: '1.7',
  maxWidth: '740px',
  sectionsCollapsed: false,
};

// --- Load + migrate ---

function migrate() {
  // Check for legacy keys and consolidate
  try {
    const legacyTypo = localStorage.getItem('teach-me-typography');
    const legacyTheme = localStorage.getItem('teach-me-theme');
    if (!legacyTypo && !legacyTheme) return null;

    const old = legacyTypo ? JSON.parse(legacyTypo) : {};
    const merged = { ...DEFAULTS };

    // Map old fontFamily full CSS string to short key
    if (old.fontFamily) {
      if (old.fontFamily.includes('OpenDyslexic')) merged.fontFamily = 'dyslexic';
      else if (old.fontFamily.includes('system-ui')) merged.fontFamily = 'sans';
      else merged.fontFamily = 'serif';
    }
    if (old.fontSize) merged.fontSize = old.fontSize;
    if (old.lineHeight) merged.lineHeight = old.lineHeight;
    if (old.maxWidth) merged.maxWidth = old.maxWidth;
    if (old.layout === 'sections') merged.sectionsCollapsed = true;
    if (legacyTheme) merged.theme = legacyTheme === 'light' ? 'light' : 'dark';

    // Save new format, delete legacy
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    localStorage.removeItem('teach-me-typography');
    localStorage.removeItem('teach-me-theme');

    return merged;
  } catch {
    return null;
  }
}

function load() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return { ...DEFAULTS, ...JSON.parse(stored) };
    // Try migration from legacy keys
    const migrated = migrate();
    if (migrated) return migrated;
  } catch {}
  return { ...DEFAULTS };
}

function save(p) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(p)); } catch {}
}

// --- Signals ---

export const prefs = signal(load());

export const effectiveTheme = computed(() => {
  const t = prefs.value.theme;
  if (t !== 'auto') return t;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
});

// --- DOM application ---

function applyToDOM(p) {
  const s = document.documentElement.style;
  s.setProperty('--font-size-base', p.fontSize);
  s.setProperty('--font-family-body', FONT_FAMILY_MAP[p.fontFamily] || FONT_FAMILY_MAP.serif);
  s.setProperty('--line-height-body', p.lineHeight);
  s.setProperty('--max-width-content', p.maxWidth);
  document.documentElement.setAttribute('data-theme', effectiveTheme.value);
}

// Auto-persist and auto-apply on any change
effect(() => {
  const p = prefs.value;
  save(p);
  applyToDOM(p);
});

// Listen for system theme changes (for 'auto' mode)
window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
  if (prefs.value.theme === 'auto') {
    document.documentElement.setAttribute('data-theme', effectiveTheme.value);
  }
});

// --- Public API ---

export function set(key, value) {
  prefs.value = { ...prefs.value, [key]: value };
}

export function reset() {
  prefs.value = { ...DEFAULTS };
}

export { FONT_FAMILY_MAP };
