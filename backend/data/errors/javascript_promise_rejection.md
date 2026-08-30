---
error_name: Unhandled Promise Rejection
language: JavaScript
category: Async Error
---

# Unhandled Promise Rejection

## Description

An unhandled promise rejection happens when a `Promise` rejects (e.g. an `await`
ed call or `fetch` fails) and no `.catch()`/`try...catch` is attached before the
promise is abandoned by the event loop. Browsers log
`Uncaught (in promise) Error: ...` / `Unhandled promise rejection`; Node prints
`UnhandledPromiseRejectionWarning` and since Node 15, an unhandled rejection
crashes the process by default.

## Common Causes

- `async` function called without `await` and without `.catch()` — if it rejects, nobody handles it.
- `fetch`/`axios`/`fs`/DB calls without error handling, especially in event handlers or `forEach`/`map` loops.
- `.then(...)` chains missing a final `.catch(...)`.
- `await` inside a `forEach` where the callback's rejection is not propagated to the surrounding `try/catch`.
- Promises created inside constructors/setup code that escape without a handler.
- A `.catch()` that itself throws.

## Example

```js
// BAD: fetch may reject; nobody handles the rejection
async function load() {
  const res = await fetch("/api/user");
  return res.json();
}

load();   // if fetch fails → Unhandled promise rejection
```

Fixed version:

```js
async function load() {
  const res = await fetch("/api/user");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

load().catch((err) => {
  console.error("Failed to load user:", err);
  renderError(err.message);
});
```

Or with `try/catch`:

```js
async function start() {
  try {
    await load();
  } catch (err) {
    console.error("Failed to load user:", err.message);
  }
}
start();
```

## Why It Happens

Promises decouple "some action" from "its outcome". When a promise rejects and no
handler consumes the rejection, the rejection is *orphaned*: nothing is waiting to
observe it, so there is no code path that could handle it later. The runtime
reports it globally (as a warning or fatal) precisely because the error would
otherwise be swallowed silently.

## Solutions

1. Read the rejection message — it identifies the async call that failed.
2. Add error handling at *every* promise-returning call: `await` inside `try/catch`, or a `.catch()` at the chain end.
3. Audit `forEach`/`map` callbacks: prefer `for...of` + `await` (rejections propagate to the outer `try`), and `.catch()` inside the callback otherwise.
4. For background tasks (timers, events, workers), always attach a `.catch()` — even if it only logs.
5. Listen for `process.on('unhandledRejection')` (Node) during development to surface them centrally.
6. Always `await` or explicitly handle promises from functions that may reject.

## Prevention

- Establish a pattern: async helpers return promises; call sites `await` them inside `try/catch`.
- Lint with `no-floating-promises` (TypeScript) to catch unhandled promises in CI.
- Prefer frameworks that centralize error handling (e.g. React error boundaries, Express middleware).
- Add tests that force the rejection path of every async operation.

## Related Errors

- `TypeError`
- `ReferenceError`
- `ECONNREFUSED` / network errors wrapped in rejections
- `SIGTERM` when Node exits due to an unhandled rejection