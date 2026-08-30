---
error_name: ZeroDivisionError
language: Python
category: Runtime Error
---

# ZeroDivisionError

## Description

`ZeroDivisionError` is raised when a number is divided or modulus'd by zero:
`10 / 0`, `x % 0`, or the floored `//` with a zero divisor. It is a subclass of
`ArithmeticError`. Unlike Java's floating-point, Python follows IEEE 754 for
`float` division by zero — `10.0 / 0.0` returns `inf`, but *integer* division and
modulo by zero always raise.

## Common Causes

- Dividing by a computed denominator that can legitimately be zero (a count, a total, a user-entered quantity).
- `statistics.mean()` of an empty list (internally divides by `len > 0` check fails).
- Averaging percentages where the sum of weights is zero.
- Modulo on a divisor read from input or config without validation.
- Dividing after subtraction that can produce exactly `0` (e.g. `(a - b) / (a - b)`).

## Example

```python
def average_price(items):
    return sum(items) / len(items)     # BAD: ZeroDivisionError on empty list
```

Fixed version:

```python
def average_price(items):
    if not items:
        return 0.0
    return sum(items) / len(items)
```

Division by a live value:

```python
count = get_count()                     # BAD: could be 0

percentage = (part / count) * 100 if count else 0.0
```

## Why It Happens

Integer division (`/`, `//`, `%`) over the integers has no defined result for a
zero divisor. Python opts for an explicit exception here rather than returning a
sentinel, because silently producing `inf`/garbage for integer math would corrupt
downstream logic. The traceback shows exactly the division expression, so the fix
is usually "guard the denominator".

## Solutions

1. Focus on the failing line — the divisor expression is the bug container.
2. Guard the divisor: `if divisor == 0` yields a fallback, or special-case the result.
3. For averages use helper patterns that return a default for empty input.
4. Replace bare denominators with validated accessors that define zero behavior.
5. When computing shares/percentages compare `denominator > 0` (counts can't be negative).
6. Add regression tests with the zero-dividend input that triggered the bug.

## Prevention

- Never trust computed denominators; treat zero as a first-class branch.
- Write property tests including `0`, empty lists, and negative values.
- Prefer functions that encode their zero behavior (`def ratio(a, b): return a / b if b else 0.0`).
- In reports/visualizations, hide or annotate undefined ratios rather than crashing.

## Related Errors

- `ValueError`
- `TypeError`
- `ArithmeticException` (Java)
- `OverflowError`