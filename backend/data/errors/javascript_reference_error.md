---
error_name: ReferenceError
language: JavaScript
category: Runtime Error
---

# ReferenceError

## Description

`ReferenceError` is thrown when code tries to read a *binding* that does not exist
in scope: `ReferenceError: name is not defined`. It is JavaScript's "unknown
identifier" error. A special sub-case is `Cannot access 'x' before initialization`
— accessing a `let`/`const` binding in its temporal dead zone before the line that
initializes it runs.

## Common Causes

- Using a variable before declaring it, or with a typo: `itemCount` vs `item_count`, `eventHandler` vs `onClick`.
- Referencing a function scoped to a module from global code (missing `export`/`import`).
- `let`/`const` used before their initialization line in the same block.
- Shadowing: an outer variable is fine but an inner `let` shadows `undefined` in a closure.
- Calling a function defined in a sibling script tag/module that never loaded.
- Variable hoisting confusion: `var` is hoisted (undefined), `let`/`const` are hoisted but in a dead zone.

## Example

```js
// BAD
function render() {
  return name.toUpperCase();   // ReferenceError: name is not defined
}
```

Fixed version:

```js
function render(name) {
  if (name == null) return "";
  return name.toUpperCase();
}
```

Temporal dead zone:

```js
console.log(count);   // ReferenceError: Cannot access 'count' before initialization
const count = 10;
```

## Why It Happens

JavaScript resolves every identifier against the current *scope chain* at
execution time. If the binding is absent from the local, closure, module, and
global scopes, the engine cannot produce a value and throws `ReferenceError`
rather than inventing one. The "before initialization" variant exists because
`let`/`const` regions are reserved even before their assignment executes.

## Solutions

1. The message names the identifier — search both the failing file and module boundaries for it.
2. For `Cannot access 'x' before initialization`, move the `const`/`let` above the code that reads it.
3. Check imports/exports: `import { helper } from "./helper.js"` (`export function helper`).
4. Beware of stale bundles or cache: hard-reload; a missing global from a previous script explains flaky references.
5. If it happens only in some tests, confirm the test file is isolated (no accidental reliance on globals).
6. Use `typeof x !== "undefined"` guards in code that bridges environments (browser globals, worker bridges).

## Prevention

- Declare variables with `const`/`let` as late as possible, near first use.
- Avoid relying on implicit globals; lint with ESLint's `no-undef`.
- Use modules (`import`/`export`) instead of shared globals.
- Let TypeScript catch undefined identifiers at compile time.

## Related Errors

- `TypeError`
- `SyntaxError`
- `NameError` (Python)
- `UnboundLocalError`