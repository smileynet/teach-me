import { h } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';
import { getTopicState } from './store.js';

const html = htm.bind(h);

/**
 * GenButton — the primary call-to-action for a topic node on a map page.
 *
 * Two orthogonal axes decide what to show (ADR 0014):
 *   - content existence (does a lesson file exist? → `lessonPath`) picks the verb
 *   - learner progress (`status`) only ever styles the label, never hides the lesson
 *
 * So a present `lessonPath` ALWAYS wins — a shipped lesson is openable regardless of
 * whether the learner has started it. Only when no lesson exists do we offer to
 * generate one.
 *
 * Generation is HONEST: this workspace has no server-side content generator wired up,
 * so instead of faking a stream we hand the user the exact prompt to run with an agent
 * in this repo (Kiro CLI, Claude Code, Codex, ...). The agent does the real work.
 */
export function GenButton({ topicId, topicTitle, topicSlug, lessonPath }) {
  const state = getTopicState(topicId);
  const [showPrompt, setShowPrompt] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!state) return null;

  // A shipped lesson is always openable — this must come BEFORE the status check.
  if (lessonPath) {
    return html`<a href=${lessonPath} class="btn primary" aria-label=${'Open lesson: ' + topicTitle}>Open lesson →</a>`;
  }

  // No lesson on disk. If the learner already marked it complete without a file, say so.
  if (state.status.value === 'complete') {
    return html`<span class="btn done">✓ Complete</span>`;
  }

  // No lesson yet — offer the honest generate path: a prompt to run with an agent.
  const prompt = `Generate the "${topicTitle}" topic for this teaching workspace: research it from real sources, then author the lesson, reference doc, quiz, and spaced-repetition cards. Run the generate-topic skill.`;

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
    return html`<button class="btn primary" onClick=${() => setShowPrompt(true)}>Generate this topic</button>`;
  }

  return html`
    <div class="gen-prompt" role="group" aria-label=${'How to generate ' + topicTitle}>
      <p class="gen-prompt-lead">This workspace doesn't generate lessons on its own. Run this prompt with an agent in this repo (Kiro CLI, Claude Code, Codex, …):</p>
      <pre class="gen-prompt-text"><code>${prompt}</code></pre>
      <div class="gen-prompt-actions">
        <button class="btn primary" onClick=${copyPrompt}>${copied ? '✓ Copied' : 'Copy prompt'}</button>
        <button class="btn" onClick=${() => setShowPrompt(false)}>Close</button>
      </div>
      <span class="sr-only" aria-live="polite">${copied ? 'Prompt copied to clipboard' : ''}</span>
    </div>
  `;
}
