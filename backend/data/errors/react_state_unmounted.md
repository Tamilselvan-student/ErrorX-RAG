---
error_name: State Update on Unmounted Component
language: React
category: React Error
---

# State Update on Unmounted Component

## Description

`Warning: Can't perform a React state update on an unmounted component ...` is a
development-mode warning emitted when a component calls `setState` (or a hook
setter) *after* React removed it from the tree — e.g. an async `fetch` or a
`setTimeout` resolves after the user navigated away. It is a *warning*, not an
error that crashes — but it signals a real leak: memory and work happen for an
invisible component.

## Common Causes

- An `async` effect that sets state after `fetch`/`axios`/`setTimeout` resolves, while the user already unmounted the component.
- Event listeners or subscriptions (WebSocket, store) registered in `useEffect` and never cleaned up.
- A `setInterval`/`setTimeout`, animation loop, or `IntersectionObserver` not cleared in the effect's cleanup.
- Routing (client-side navigation) unmounting a page whose pending requests keep setting state.
- State set in a callback invoked later (e.g. a debounced input handler) with no mounted-guard.

## Example

```jsx
// BAD — fetches can resolve after unmount
useEffect(() => {
  fetchUser(id).then((u) => setUser(u));   // setState on unmounted component
  // no cleanup / cancellation
}, [id]);
```

Fixed — use the effect's cleanup to cancel:

```jsx
useEffect(() => {
  let cancelled = false;                    // clean marker for "already unmounted"
  fetchUser(id).then((u) => {
    if (!cancelled) setUser(u);
  });
  return () => {
    cancelled = true;                       // runs on unmount & deps change
  };
}, [id]);
```

Or with an `AbortController`:

```jsx
useEffect(() => {
  const ctrl = new AbortController();
  fetch(`/api/user/${id}`, { signal: ctrl.signal })
    .then((r) => r.json())
    .then(setUser)
    .catch((err) => { if (err.name !== "AbortError") setError(err); });
  return () => ctrl.abort();
}, [id]);
```

## Why It Happens

React's lifecycle is: render → commit → (possibly) unmount. Closing over `setUser`
in an async callback is legal, but React 18 still warns when the *committed fiber*
is gone: updating a destroyed fiber's state is pointless and usually means cleanup
was skipped, or that an effect leaks a subscription the browser or bundle cannot
garbage-collect.

## Solutions

1. Cancel async work in the effect cleanup (AbortController for fetch, clear timers, removeEventListeners, unsubscribe stores).
2. Use a `mounted`/`cancelled` flag set in the cleanup and checked before every `setState` after `await`.
3. Move long-lived subscriptions out of single components into a store/context that survives unmounts.
4. For timers/polls, always `setInterval` + `clearInterval` in cleanup.
5. If using react-query/SWR for data, prefer their built-in cancellation/invalidation instead of hand-rolled effects.
6. Treat the warning as a signal of a leak: it usually accompanies subscriptions or listeners that should be torn down.

## Prevention

- Establish a "setState after await" code-review rule with a cleanup.
- Abstract the canceled-request pattern into a small `useAsync`-style hook used everywhere.
- Keep effects focused: one effect = one subscription with an explicit cleanup.
- Enable Strict Mode in development to surface double-invoked effects and forgotten cleanups.

## Related Errors

- `Invalid Hook Call`
- `Invalid Hook Order`
- Memory-leak-related symptoms (listeners accumulating)
- `Error: Too many re-renders` (a different but nearby lifecycle bug)