// typography-prefs.js — BLOCKING script, must load in <head> before CSS renders.
// Reads user preferences from localStorage and applies CSS custom properties
// on documentElement to prevent FOUC (flash of unstyled content).
// Keep this file tiny (< 1KB minified).
(function() {
  try {
    var prefs = JSON.parse(localStorage.getItem('teach-me-typography'));
    if (!prefs) return;
    var s = document.documentElement.style;
    if (prefs.fontSize) s.setProperty('--font-size-base', prefs.fontSize);
    if (prefs.fontFamily) s.setProperty('--font-family-body', prefs.fontFamily);
    if (prefs.lineHeight) s.setProperty('--line-height-body', prefs.lineHeight);
    if (prefs.maxWidth) s.setProperty('--max-width-content', prefs.maxWidth);
  } catch(e) {}
})();
