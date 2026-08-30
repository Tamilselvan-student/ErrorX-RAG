---
error_name: TypeError
language: JavaScript
category: Runtime Error
---

# TypeError

## Description

`TypeError` occurs when a JavaScript *value* is not of the type an operation
expects — calling something that isn't a function, reading a property of
`undefined`/`null`, or passing an invalid value to an API (e.g. `new Date(2024, 13)`).
The classic message is `Cannot read properties of undefined (reading 'x')` — which
means you tried to access `.x` on an *undefined* value.

## Common Causes

- Accessing a property on `undefined` or `null`: `user.name` when `user` is undefined.
- Calling a value as a function: `const f = undefined; f();` → `f is not a function`.
- Calling a method on a `null` result of `document.querySelector`/`getElementById`/`JSON.parse` failure.
- Destructuring or indexing too deep into an object that is missing a branch.
- Assigning a value of the wrong shape from an API response without validation.
- Using `for...of`/array methods on a `null` array-like.

## Example

```js
// BAD
const profiles = await api.fetchProfiles();   // returns undefined for missing user
const name = profiles[0].name.toUpperCase();   // TypeError: Cannot read properties of undefined
```

Fixed version:

```js
const profiles = await api.fetchProfiles();
const first = profiles?.[0]?.name;
const name = first ? first.toUpperCase() : "Unknown";
```

Or with explicit handling:

```js
if (!profiles || profiles.length === 0) {
  throw new Error("No profile found");
}
const name = profiles[0].name;
```

## Why It Happens

JavaScript is dynamically typed: `undefined` and `null` are real, pass-around
values. Accessing a property requires an *object*, so when the runtime tries to
carry out `undefined.name` it has nothing to index. Modern engines phrase this as
"Cannot read properties of undefined (reading 'name')" precisely so you can find
both the value (`undefined`) and the property (`name`) in one message.

## Solutions

1. Read both parts of the message: which property (`reading 'x'`) and which kind of missing value (`undefined` or `null`).
2. Use optional chaining `obj?.a?.b` and nullish coalescing `?? default` to tolerate gaps safely.
3. Guard array access: `arr?.[0]` or `if (Array.isArray(arr) && arr.length)`.
4. Validate API responses at the boundary (schema checks) so downstream code trusts the shape.
5. Log the offending value once (`console.debug("profiles =", profiles)`) to see the actual runtime shape.
6. When the value must exist, throw a descriptive error instead of letting the TypeError travel.

## Prevention

- Prefer TypeScript (or JSDoc `@type`) plus runtime validation for external data.
- Design functions to never leak raw `undefined` for shapes you control.
- Add tests for the "missing field" and "empty array" response variants.
- Enable `noUncheckedIndexedAccess` if using TypeScript — it surfaces these statically.

## Related Errors

- `ReferenceError`
- `RangeError`
- `NullPointerException` (Java idea)
- `AttributeError` (Python idea)