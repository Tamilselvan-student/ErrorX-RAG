---
error_name: Invalid Hook Order
language: React
category: React Error
---

# Invalid Hook Order

## Description

"Rendered more hooks than during the previous render" (or fewer) is React's *Rules
of Hooks* violation: the *number/order* of hooks a component calls changed between
two renders. React matches each render's hook calls to the previous one **by
position** — when the count changes, React cannot tell which state belongs to
which call and throws. The message:
`Rendered more hooks than during the previous render.`

## Common Causes

- Hooks nested inside a conditional — one render runs the hook, the next skips it:

```jsx
function Profile({ isAdmin }) {
  if (isAdmin) {
    const [level, setLevel] = useState(1);  // BAD: hook in a conditional branch
  }
  return <p>Profile</p>;
}
```

- Hooks inside loops or early returns (`return <Loading/>` before a `useEffect`).
- Deriving hook presence from `props`/state that changes across renders.
- Calling a hook inside a sub-render helper that conditionally unmounts.
- Custom hooks that conditionally call other hooks.

## Example

```jsx
// BAD — hook count differs between renders
function Toggle({ useExtra }) {
  const [on, setOn] = useState(false);
  if (useExtra) {
    const [extra, setExtra] = useState("");   // appears/disappears → order violation
  }
  return <button onClick={() => setOn((v) => !v)}>{on ? "ON" : "OFF"}</button>;
}
```

Fixed version — unconditional hooks, conditional *values*:

```jsx
function Toggle({ useExtra }) {
  const [on, setOn] = useState(false);
  const [extra, setExtra] = useState("");      // always called
  const effective = useExtra ? extra : null;   // conditionally *used*, not called
  return <button onClick={() => setOn((v) => !v)}>{on ? "ON" : "OFF"}</button>;
}
```

## Why It Happens

React stores a component's hook state in a linked list inside its fiber. On each
render the reconciler replays the hook calls and *zips* them with the list in
order: 1st `useState` ↔ 1st slot, 2nd ↔ 2nd slot, etc. If the count varies, the
zip misaligns — slot 1 from the old render may pair with a different logical hook,
so state would be corrupted. React refuses to proceed and reports the count change.

## Solutions

1. Locate the conditional/loop/early-return that wraps a hook.
2. Move every hook to unconditional top-level code; guard only the *use* of values, not the hook calls.
3. If you need "call only sometimes", split into child components — React remounts a separate fiber with its own hook list, which is legal.
4. Check custom hooks for internal conditionals that call hooks.
5. After fixes, test the toggle-producing render path (both branches) against the error.

## Prevention

- `eslint-plugin-react-hooks` with `rules-of-hooks` (and `exhaustive-deps`) enabled.
- Review hook placement in code review: hooks belong between the signatures and any conditional logic.
- Extract conditionally-available features into their own components.
- Rule of thumb: *hook calls are unconditional; only data flows conditionally*.

## Related Errors

- `Invalid Hook Call`
- `Error: Too many re-renders`
- `Maximum update depth exceeded`
- `Invalid React Element`