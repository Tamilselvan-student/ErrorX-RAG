---
error_name: Invalid React Element
language: React
category: React Error
---

# Invalid React Element

## Description

`Element type is invalid: expected a string (for built-in components) or a
class/function (for composite components) but got: object.` happens when a
JSX/`React.createElement` receives something that is not a valid component type —
most commonly *two copies of React* (one component created by a different React
copy than the reconciler running), an unimported component (`undefined`), or a
non-component value passed as `<thing/>`.

Common variants:
`Element type is invalid: expected a string ... but got: undefined` — your
import is missing/wrong; and the "object" variant usually signals a duplicate
React module.

## Common Causes

- Importing a component incorrectly: `import Button from './Button'` when the file exports a *named* export `export const Button` (results in `undefined`).
- Forgetting to import a component used in JSX (typos resolve to undefined in some setups).
- Two copies of `react` loaded (duplicated dependency, ESM/CJS interop), so a component built with one copy is rendered by the other.
- Passing a **rendered element** instead of a component type: `<Route element={<Dashboard/>}/>` vs `<Route component={<Dashboard/>}` misuse, or `createElement(<Foo/>)` instead of `createElement(Foo)`.
- Dropping a default-exported component into a dynamic import that returns `{ default: Component }`.

## Example

```jsx
// BAD: named export imported as default
// Button.jsx
export const Button = ({ children }) => <button>{children}</button>;

// App.jsx
import Button from "./Button";   // undefined!
export default function App() {
  return (
    <div>
      <Button>Save</Button>      // Element type is invalid: ... but got: undefined
    </div>
  );
}
```

Fixed:

```jsx
import { Button } from "./Button";   // GOOD: named import
```

Or for dynamic imports:

```jsx
const { default: Dashboard } = await import("./Dashboard");
```

## Why It Happens

React JSX compiles to `React.createElement(type, props)`. At render time the
reconciler must resolve `type` to a string (DOM tag), or a function/class
(component). When the module resolution yields `undefined` (bad import) or an
object (a fiber/element from a *different* React copy — `Symbol.for('react.element')`
mismatch), the reconciler has no way to render it and throws this error.

## Solutions

1. Read the "but got" value: `undefined` → import problem; `object` → duplicate React problem.
2. For `undefined`: verify the export name/style (`export default` vs `export const`) and the import spelling/casing.
3. For `object`: run `npm ls react` and dedupe (`npm dedupe`), or add a `resolve.alias` in Vite/webpack pointing react to one copy.
4. Check where `React.createElement(<Thing/>)` or `<Thing/>` with a pre-rendered element appears — pass the *component*, not an element.
5. Restart dev servers after dependency changes; stale HMR graphs can show this error once code changes types.
6. Add a fallback in dynamic-import boundaries: `(mod) => mod.default ?? mod`.

## Prevention

- Prefer named exports for components, or consistently default exports — never both for the same component.
- Use single React version everywhere (`peerDependencies`, workspaces with hoisting).
- TypeScript catches undefined component references at compile time.
- A tiny "react-in-repo" test (`import React` resolves to the same file) finds duplicates cheaply.

## Related Errors

- `Invalid Hook Call`
- Sibling errors from duplicate React (`hooks` plus `element type`)
- `ReferenceError` when imports are absent
- `Files differ`-class toolchain errors