# Shared Data, Multiple Views — Architecture Research

## Summary

Render one dataset as multiple views by keeping a single **source of truth** (the raw data + a few input signals like filter/sort/selection) and **deriving** every view's data on each render — never storing a second copy. A shared presentational component accepts a `layout`/`variant` prop (or is composed differently) so the same card renders in two layouts. The dominant pitfall is duplicated/stored derived state, which produces synchronization bugs and prop drift; the fix is "store the minimal set, derive the rest," memoizing only the expensive derivations.

## Details

### 1. Single source of truth + derived projections (the core pattern)

- Store only what's irreducible: the **raw dataset**, plus **input signals** (search query, selected filter, sort key, selection). Everything else — filtered lists, counts, "is valid," a depth-0 subset — is **derived on each render** from those. (Kinney, "Derived vs Stored State"; multiple Medium/freeCodeCamp SSOT articles.)
- This is the frontend analogue of MVVM: the **view-model** is a *value converter* that exposes/projects the model so views can consume it easily; the model stays the single source of truth and views are kept in sync by re-derivation, not manual mirroring. (Wikipedia MVVM; MSDN MVVM.)
- Deriving a **depth-0 subset** from one dataset is just a client-side projection:
  ```js
  const roots = useMemo(
    () => nodes.filter(n => n.depth === 0),
    [nodes]
  );
  ```
  The list view consumes `roots`; the graph/map view consumes the full `nodes` + `edges`. One store, two projections — no second state variable.
- **Selector / custom-hook extraction:** for reusable projections, wrap the derivation in a hook (`useFilteredAndSortedData(data, filterFn, sortKey)`) that returns a `useMemo`'d result. This is the React equivalent of Redux/Reselect *selectors* — a named, testable projection function over the store. (Kinney; Reselect pattern.)

### 2. One shared card component, two layouts

- **Layout-prop pattern ("dual view"):** a single `ProjectItem({ item, layout })` (or `isGrid` boolean) branches only on *presentation* — grid renders a compact card, carousel/list renders a full-width row. **Same data, same component, two outputs.** The two container views (`ProjectGrid`, `ProjectView`) both `.map()` the same imported array into the shared item. A `ViewToggle` (persisted to `localStorage`) flips one signal. (sammii, "One component, two layouts.")
- Works well when: the data is **identical** across views and the difference is purely presentational (density: scan vs. read); same data serves different interaction models (browse vs. deep-dive).
- **Split into two components instead** when: (a) the branch prop starts controlling more than layout (data fetching, event handling, children) — "two components wearing one coat"; (b) performance matters — both branches mount/render even when one is hidden, so large/heavy lists favor lazy-loaded separate impls; (c) the **data shapes diverge** (grid wants a summary, detail wants the full object) → the shared prop surface grows awkward. Rule of thumb: shallow branching + identical data = one component; passing the layout flag 3 levels deep = reach for composition. (sammii.)

### 3. Pitfalls

- **Duplicated / stored derived state (the #1 trap):** storing `total`, `filteredList`, `count`, or a `depth0Subset` in their own `useState` means every mutation must remember to update *all* copies. Miss one path (e.g. `removeItem`) and the UI shows inconsistent data. Symptoms: synchronization bugs, extra re-renders (N `setState` calls per change), higher memory. Fix: derive them. (Kinney; freeCodeCamp "Shared State Complexity.")
- **Prop drift / awkward prop surface:** when two layouts share a component but their data needs diverge, the component grows optional/conditional props that only one view uses — the shape "drifts" apart. Sign to split. (sammii.)
- **Over-memoization:** `useMemo` has its own overhead; only memoize *expensive* derivations (filter/sort over large lists), not cheap ones (`.length`). Profile first. (Kinney; Feature-Sliced "When to useMemo.")
- **Two sources of truth for the same fact:** e.g. URL state *and* mirrored `useState` — pick one authoritative source (often the URL) and derive the rest, or the two fight over precedence. (SO: reconcile setState with URL as SSOT.)
- **Hydration mismatch** when the view choice comes from `localStorage`: guard SSR reads (`typeof window !== 'undefined'`) so the first render matches. (sammii.)

## Sources

- [Derived vs Stored State — Steve Kinney](https://www.stevekinney.com/courses/react-performance/derived-vs-stored-state) — "store the minimal state, derive everything else"; shopping-cart + user-management filter/sort examples; custom-hook selectors; useMemo trade-offs.
- [One component, two layouts: the dual view pattern in React — sammii](https://sammii.hashnode.dev/one-component-two-layouts-the-dual-view-pattern-in-react) — shared data file + `ProjectItem({isGrid})` rendered as grid vs. carousel; when the pattern breaks (split into two components).
- [Model–view–viewmodel — Wikipedia](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel) — viewmodel as "value converter"/projection of the model.
- [Model-View-ViewModel — Microsoft .NET docs](https://learn.microsoft.com/en-us/dotnet/architecture/maui/mvvm) — model = source of truth; VM exposes/encapsulates it for the view.
- [Shared State Complexity in React — freeCodeCamp](https://www.freecodecamp.org/news/shared-state-complexity-in-react-handbook/) — shared-state problem, sync cost as apps grow.
- [Understanding Derived State in React — Medium](https://lasalshettiarachchi458.medium.com/understanding-derived-state-in-react-when-and-why-to-use-it-0184bf8b9ea8) — derived state ⇒ single source of truth, avoid duplication.
- [When to useMemo: A React Performance Guide — Feature-Sliced Design](https://feature-sliced.design/blog/react-usememo-optimization) — memoize expensive derived data; blind use adds overhead.
- [How to reconcile setState with URL as single source of truth — Stack Overflow](https://stackoverflow.com/questions/62724853/how-to-reconcile-reacts-setstate-with-using-the-url-as-the-single-source-of-tru) — avoid two competing sources of truth.
