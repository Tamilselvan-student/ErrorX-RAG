---
error_name: RangeError
language: JavaScript
category: Runtime Error
---

# RangeError

## Description

`RangeError` is thrown when a numeric *value* is outside the allowed range for an
operation — a number that is too large/small, an invalid array length, an
impossibly deep call stack, or an out-of-range index for typed arrays and strings.
The message states the constraint: `Invalid array length`, `Maximum call stack size
exceeded`, or `Maximum call stack size exceeded at ...`.

## Common Causes

- Recursion without a terminating condition (`Maximum call stack size exceeded`).
- `new Array(-1)` or `new Array(4294967295 ** 2)` — invalid length.
- `toFixed(digits)` with `digits` outside 0–100, or `-[1]` typed-array index out of bounds.
- Extremely large numbers passed to `String.prototype.repeat`, `Array.prototype.flat` beyond depth.
- `Date` values that overflow range in some engines/contexts.
- Custom recursion tools (JSON.stringify of a circular object) that blow the stack.

## Example

```js
function countdown(n) {
  // BAD: no base case — recursion never ends
  return countdown(n + 1);
}
countdown(1);
// RangeError: Maximum call stack size exceeded
```

Fixed version:

```js
function countdown(n) {
  if (n >= 10) return n;          // base case stops the recursion
  return countdown(n + 1);
}
countdown(1);
```

Invalid array length:

```js
const arr = new Array(-5);        // BAD: RangeError: Invalid array length
```

## Why It Happens

The engine enforces hard limits for certain operations: array lengths are unsigned
32-bit limited, `toFixed` digits are bounded 0–100, and each call to a function
consumes a fixed-size call stack. When the requested value or recursion depth
hits the limit, the engine cannot honor the request and fails with `RangeError` —
protecting the process from unbounded memory use.

## Solutions

1. For `Maximum call stack size exceeded`: the trace's repeated frames reveal the recursion cycle — add a base case or convert to an explicit loop.
2. For `Invalid array length`: clamp the computed length to valid bounds (`Math.max(0, Math.min(maxLen, value))`).
3. Guard `toFixed`/`repeat`/`flat` arguments with validated ranges.
4. Serialize circular structures with a seen-set (`WeakSet`) instead of letting `JSON.stringify` recurse.
5. Replace deep recursion for large inputs with iterative implementations.
6. Add an explicit recursion depth counter that fails fast with a clear error.

## Prevention

- Prefer loops to recursion for unbounded iteration.
- Encode validation for numeric arguments directly in your API signatures.
- Test with the boundary values that the engine specifies (0, 1, max).
- Keep serialization data acyclic by design.

## Related Errors

- `TypeError`
- `StackOverflowError` (Java idea)
- `RecursionError` (Python)
- `Invalid array length` (specific case)