# Reference Repos

`.references/` is gitignored. Clone these to rehydrate after a fresh checkout.

## Rehydrate All

```bash
# Run from project root
git clone --depth 1 https://github.com/mattpocock/skills.git .references/mattpocock-skills
git clone --depth 1 https://github.com/mingrammer/diagrams .references/diagrams
git clone --depth 1 https://github.com/cduck/drawsvg .references/drawsvg
git clone --depth 1 https://github.com/terrastruct/d2 .references/d2
git clone --depth 1 https://github.com/orsinium-labs/svg.py .references/svg-py
git clone --depth 1 https://github.com/Kozea/pygal .references/pygal
git clone --depth 1 https://github.com/xflr6/graphviz .references/graphviz-python
git clone --depth 1 https://github.com/archwright-ai/archwright .references/archwright
git clone --depth 1 https://github.com/fay-i/mermaid-mcp .references/mermaid-mcp
git clone --depth 1 https://github.com/microsoft/playwright-mcp .references/playwright-mcp
```

## Individual Repos

| Directory | Repo | Why it's here |
|-----------|------|---------------|
| `mattpocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills) | Origin of teach/wait-what/quiz-me skills. Study for teaching patterns and formats. |
| `diagrams` | [mingrammer/diagrams](https://github.com/mingrammer/diagrams) | Python architecture diagram DSL (42k★). Extracted: fan-out edges, presets, context manager patterns. |
| `drawsvg` | [cduck/drawsvg](https://github.com/cduck/drawsvg) | Primary SVG generation library. Our `draw-diagram.py` uses it. |
| `d2` | [terrastruct/d2](https://github.com/terrastruct/d2) | Diagram scripting language (24k★). Used for auto-layout diagrams. |
| `svg-py` | [orsinium-labs/svg.py](https://github.com/orsinium-labs/svg.py) | Type-safe Python SVG library. Alternative to drawsvg if needed. |
| `pygal` | [Kozea/pygal](https://github.com/Kozea/pygal) | Pure Python SVG charting. Reference for interactive SVG patterns. |
| `graphviz-python` | [xflr6/graphviz](https://github.com/xflr6/graphviz) | Python Graphviz bindings. Optional backend for complex auto-layout (ticket 010). |
| `archwright` | [archwright-ai/archwright](https://github.com/archwright-ai/archwright) | Architecture audit tool. Cloned for visual prior art (none found — basic HTML reports only). |
| `mermaid-mcp` | [fay-i/mermaid-mcp](https://github.com/fay-i/mermaid-mcp) | Local Mermaid MCP server. Evaluated and skipped (ticket 009). Keep for reference. |
| `playwright-mcp` | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Official Playwright MCP. Our browser agent uses this. Key reference for tool capabilities. |
