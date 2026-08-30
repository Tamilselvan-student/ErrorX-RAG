---
error_name: Type Mismatch Error
language: JavaScript
category: Runtime Error
---

# Type Mismatch Error

## Description

JavaScript error messages often mention a *type mismatch* between what a function
expects and what it received: `argument is not a function`,
`Expected Number, got String`, `begin/end arguments must be of same type` (in slice
code), `first argument must be a string or Buffer`. These almost always trace back
to data arriving in a different shape than the code assumes — the raw payload was
a string where a number was needed, or an object where an array was expected.

## Common Causes

- Parsing form/query params with the wrong decoder: everything arrives as strings, but the code expects numbers.
- `JSON.parse`-ing into a shape that does not match what the backend actually sends.
- `Array.prototype.map`/`reduce` over an object (or object over an array) because of an unvalidated response.
- Passing a DOM/Node value where a primitive is required (`...args` from `arguments`).
- Using `+` to concat numbers from `parseInt` that returned `NaN`.
- Mixed-type comparisons feeding sorting/filter logic with inconsistent coercion.

## Example

```js
// BAD
function double(n) {
  return n * 2;
}

const price = getQueryParam("price");   // returns "5" (a string)
const doubled = double(price);          // "5" * 2 → 10 by coercion, but:
```

The dangerous variant — string concat hides the bug:

```js
function total(a, b) {
  return a + b;       // if a and b are strings: "2" + "3" = "23"
}
```

Fixed version — parse at the boundary:

```js
function total(a, b) {
  const na = Number(a);
  const nb = Number(b);
  if (!Number.isFinite(na) || !Number.isFinite(nb)) {
    throw new TypeError(`expected numbers, got ${a} (${typeof a}) and ${b} (${typeof b})`);
  }
  return na + nb;
}

const result = total(getQueryParam("a"), getQueryParam("b"));
```

## Why It Happens

JavaScript coerces types implicitly in many operators (`+` concatenates when a
string is present, comparisons can convert), so a mismatched type rarely throws
immediately — instead it produces a wrong value that only *later* violates a
function's expectations. Type errors surface when a function performs an operation
its argument's type cannot support, or when the coerced value (like `NaN`) flows
into logic that assumed a number.

## Solutions

1. Identify the "expected vs got" pair in the message; find where the got-value entered your code.
2. Print `typeof` and the raw value at the boundary (query params, JSON responses, config) to confirm the shape.
3. Parse/validate near the input: `Number(param)`, schema-validate JSON (zod), or constructor factories.
4. When concatenating user data, choose explicit `String(...)` or template literals so coercion is intentional.
5. Guard with checks that throw descriptive errors instead of letting `NaN`/`undefined` wander.
6. After fixing, test the actual payload from the failing request, not the idealized fixture.

## Prevention

- TypeScript (or JSDoc) plus runtime validation for anything external.
- Single decode helpers for query/form/JSON so parsing rules live in one place.
- Adopt a strict "no implicit coercion" convention (`===`, explicit conversions).
- Regression-test with the exact data shape from the live failure.

## Related Errors

- `TypeError`
- `RangeError`
- `ValueError` (Python)
- `NumberFormatException` (Java)