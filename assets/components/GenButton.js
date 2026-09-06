import { h } from 'preact';
import htm from 'htm';
import { getTopicState } from './store.js';
import { GeneratePrompt } from './GeneratePrompt.js';

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
 * generate one, honestly: a prompt to run with an agent in this repo (GeneratePrompt).
 */
export function GenButton({ topicId, topicTitle, topicSlug, lessonPath }) {
  const state = getTopicState(topicId);

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
  return html`<${GeneratePrompt} buttonLabel="Generate this topic" groupLabel=${'How to generate ' + topicTitle} prompt=${prompt} />`;
}
