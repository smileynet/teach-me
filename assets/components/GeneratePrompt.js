import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

/**
 * GeneratePrompt — the honest "run this prompt with an agent" panel.
 *
 * This workspace has no server-side content generator, so instead of faking a
 * stream (or navigating to a page that doesn't exist yet) we hand the user the
 * exact prompt to run with an agent in this repo. The agent does the real work.
 *
 * Renders a `Generate …` button; clicking it reveals the prompt + a copy button.
 *
 * Props:
 *   buttonLabel — text for the reveal button (e.g. "Generate this topic", "+ Generate quiz")
 *   groupLabel  — accessible group label for the revealed panel
 *   prompt      — the exact prompt string to run with an agent
 */
export function GeneratePrompt({ buttonLabel, groupLabel, prompt }) {
  const [showPrompt, setShowPrompt] = useState(false);
  const [copied, setCopied] = useState(false);

  function copyPrompt() {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(prompt).then(flagCopied);
    } else {
      const ta = document.createElement('textarea');
      ta.value = prompt;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      flagCopied();
    }
  }

  function flagCopied() {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (!showPrompt) {
    return html`<button class="btn primary" onClick=${() => setShowPrompt(true)}>${buttonLabel}</button>`;
  }

  return html`
    <div class="gen-prompt" role="group" aria-label=${groupLabel}>
      <p class="gen-prompt-lead">This workspace doesn't generate content on its own. Run this prompt with an agent in this repo (Kiro CLI, Claude Code, Codex, …):</p>
      <pre class="gen-prompt-text"><code>${prompt}</code></pre>
      <div class="gen-prompt-actions">
        <button class="btn primary" onClick=${copyPrompt}>${copied ? '✓ Copied' : 'Copy prompt'}</button>
        <button class="btn" onClick=${() => setShowPrompt(false)}>Close</button>
      </div>
      <span class="sr-only" aria-live="polite">${copied ? 'Prompt copied to clipboard' : ''}</span>
    </div>
  `;
}
