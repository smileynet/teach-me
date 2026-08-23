import { h, render } from 'preact';
import { useState, useEffect } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

/**
 * CodeBlockToolbar — progressive enhancement for pre[data-file] elements.
 *
 * Adds copy + download buttons to code blocks that have a data-file attribute.
 * - Copy: extracts clean text (diff-aware — strips removed lines and markers)
 * - Download: conditional — only shown if the reference file exists (HEAD check)
 *
 * Exports:
 *   initCodeBlockToolbar() — queries all pre[data-file] and mounts toolbars.
 *
 * Called by page-shell.js.
 */

// Shared state: which block currently shows "Copied!" feedback (prevents multiple)
let copiedTimeout = null;

/**
 * Extract clean code text from a code element, handling diff blocks.
 * - For diff blocks: skips removed lines (spans with --error color), strips +/- markers
 * - For complete/fragment blocks: returns textContent directly
 */
function extractCleanText(preEl) {
  const codeEl = preEl.querySelector('code');
  if (!codeEl) return preEl.textContent;

  const mode = preEl.getAttribute('data-mode');
  if (mode !== 'diff') {
    return codeEl.textContent;
  }

  // Diff mode: walk child nodes, skip removed lines, strip markers
  const lines = [];
  const raw = codeEl.innerHTML;

  // Split by lines, process each
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = raw;

  // Walk text content line by line, skipping error-colored spans
  const allText = [];
  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      allText.push({ text: node.textContent, removed: false });
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const style = node.getAttribute('style') || '';
      const isRemoved = style.includes('--error');
      if (isRemoved) {
        allText.push({ text: node.textContent, removed: true });
      } else {
        for (const child of node.childNodes) {
          walk(child);
        }
      }
    }
  }

  for (const child of codeEl.childNodes) {
    walk(child);
  }

  // Reconstruct: join text, split by newlines, filter removed, strip markers
  const fullText = allText
    .filter(t => !t.removed)
    .map(t => t.text)
    .join('');

  // Strip leading space/+/- marker from each line (diff convention)
  return fullText
    .split('\n')
    .map(line => {
      if (line.startsWith('+') || line.startsWith('-') || line.startsWith(' ')) {
        return line.slice(1);
      }
      return line;
    })
    .join('\n')
    .trim();
}

/**
 * Derive the download path for a code block's file.
 * Pattern: ../reference/code/{lesson-slug}/{filename}
 */
function getDownloadPath(fileName) {
  // Derive lesson slug from current page URL
  const path = window.location.pathname;
  const match = path.match(/(\d{4}-.+?)\.html/);
  if (!match) return null;
  const lessonSlug = match[1].replace(/^\d+-/, '');
  return `../reference/code/${lessonSlug}/${fileName}`;
}

function Toolbar({ preEl }) {
  const [copied, setCopied] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const fileName = preEl.getAttribute('data-file');
  const mode = preEl.getAttribute('data-mode');
  const isFragment = mode === 'fragment';

  // Check if download file exists (skip for fragments)
  useEffect(() => {
    if (isFragment) return;
    const path = getDownloadPath(fileName);
    if (!path) return;
    fetch(path, { method: 'HEAD' })
      .then(res => { if (res.ok) setDownloadUrl(path); })
      .catch(() => {});
  }, [fileName, isFragment]);

  function handleCopy() {
    const text = extractCleanText(preEl);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => showCopied());
    } else {
      // Fallback for non-secure contexts
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showCopied();
    }
  }

  function showCopied() {
    setCopied(true);
    if (copiedTimeout) clearTimeout(copiedTimeout);
    copiedTimeout = setTimeout(() => setCopied(false), 2000);
  }

  return html`
    <div class="code-toolbar" role="group" aria-label="Code block actions">
      <button
        type="button"
        class=${copied ? 'copied' : ''}
        onClick=${handleCopy}
        aria-label=${copied ? 'Copied!' : 'Copy code'}
      >
        ${copied ? 'Copied!' : 'Copy'}
      </button>
      ${downloadUrl && html`
        <a href=${downloadUrl} download aria-label="Download ${fileName}">
          Download
        </a>
      `}
    </div>
    ${copied && html`<span class="sr-only" aria-live="polite">Code copied to clipboard</span>`}
  `;
}

/**
 * Initialize CodeBlockToolbar on all pre[data-file] elements.
 */
export function initCodeBlockToolbar() {
  const blocks = document.querySelectorAll('pre[data-file]');
  if (!blocks.length) return;

  blocks.forEach(pre => {
    // Don't mount twice
    if (pre.querySelector('.code-toolbar')) return;

    const mount = document.createElement('div');
    mount.style.position = 'absolute';
    mount.style.top = '0';
    mount.style.right = '0';
    pre.appendChild(mount);
    render(html`<${Toolbar} preEl=${pre} />`, mount);
  });
}
