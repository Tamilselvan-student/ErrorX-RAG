---
error_name: Invalid Hook Call
language: React
category: React Error
---

# Invalid Hook Call

## Description

"Hooks can only be called inside of the body of a function component" — this error
means a React hook (`useState`, `useEffect`, `useRef`, ...) was called from a place
React does not allow: a regular function, a class component, a callback/event
handler, a loop, or a nested function. You will also see
`Error: Invalid hook call. Hooks can only be called inside of the body of a function component.`
The message even lists common causes.

## Common Causes

- Calling a hook inside an event handler or a plain helper function:

```jsx
function App() {
  function handleClick() {
    const [x, setX] = useState(0);   // BAD: inside a handler
  }
  return <button onClick={handleClick}>Go</button>;
}
```

- Calling a hook inside a `useEffect` callback, `useCallback`, or any nested function.
- Calling a hook inside a *class* component (`class App extends React.Component`).
- Calling hooks inside conditionals or loops (invalidates the ordering contract).
- Two copies of React in the app (`useState` imported from the wrong copy — the hook ecosystem mismatch the error message warns about).

## Example

```jsx
// BAD
export default function App() {
  const bad = () => {
    const [count, setCount] = useState(0);   // Invalid hook call
    setCount(1);
  };
  return <button onClick={bad}>Click</button>;
}
```

Fixed version — hooks live at the top level of the component body:

```jsx
export default function App() {
  const [count, setCount] = useState(0);      // GOOD: top level of the component

  const bad = () => setCount((c) => c + 1);   // handler only calls setState

  return <button onClick={bad}>Count: {count}</button>;
}
```

## Why It Happens

React tracks hooks by their *position* in the component's render tree via a
per-fiber hook list. Every render, React reads hooks in the same order to restore
state. Calling a hook outside the render path (in an event handler, helper,
class) breaks that positional contract — React's dispatcher is simply not set up
there — so it throws to avoid corrupting state.

## Solutions

1. Move the hook to the top level of the function component (not inside handlers, effects, conditionals, or loops).
2. If the component must use a class, use class lifecycle APIs instead of hooks.
3. Check `package.json`/bundle for duplicate React instances (`npm ls react`) — the error message lists this check.
4. For shared state logic, extract a custom hook `useXxx()` whose body calls hooks at the top level.
5. If it only happens during HMR reloads, restart the dev server / do a clean install.

## Prevention

- Lint with `eslint-plugin-react-hooks` — the official rules flag invalid placement.
- Keep a naming convention: custom hooks start with `use`.
- Keep components small so hook placement is easy to review.
- Run a fresh install/build in CI to avoid stale duplicate React artifacts.

## Related Errors

- `Invalid Hook Order` (rules of hooks)
- `Error: Too many re-renders`
- `Invalid React Element`
- `setState on an unmounted component`