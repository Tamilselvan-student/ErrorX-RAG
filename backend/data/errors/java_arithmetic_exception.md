---
error_name: ArithmeticException
language: Java
category: Runtime Error
---

# ArithmeticException

## Description

`ArithmeticException` is thrown by the JVM for exceptional arithmetic conditions.
In practice the common case is **integer division by zero**: `10 / 0` throws
`java.lang.ArithmeticException: / by zero`. Floating-point division by zero does
`not` throw — `10.0 / 0` yields `Infinity`, which is why this error surprises
people who expect a crash everywhere.

## Common Causes

- Integer division/modulo by a variable that is zero (`x / y`, `x % y`).
- Computing a denominator from untrusted input (client-provided quantities, counts from a query that may be 0).
- `BigDecimal.divide(...)` without a `MathContext` producing a non-terminating decimal.
- Using `%` or `/` with a value derived from `args` or configuration without validation.

## Example

```java
int total = 100;
int parts = getParts();          // may return 0

int perPart = total / parts;     // BAD: ArithmeticException: / by zero
```

Fixed version:

```java
int total = 100;
int parts = getParts();

if (parts == 0) {
    System.out.println("Cannot divide — parts is zero.");
} else {
    int perPart = total / parts;
    System.out.println(perPart);
}
```

Alternative that avoids branches with a safe average:

```java
int perPart = parts == 0 ? 0 : total / parts;
```

## Why It Happens

Integer division by zero is mathematically undefined and, in two's-complement
arithmetic, has no valid machine result, so the JVM throws instead of silently
producing garbage. The `BigDecimal` variant throws when a division cannot be
represented finitely (e.g. `1 / 3`) without a rounding context.

## Solutions

1. Locate the `/` or `%` operand in the stack trace; the message `/ by zero` tells you the divisor came out to zero.
2. Guard the divisor before the operation, or special-case zero gracefully.
3. `populate the MathContext` when using `BigDecimal`: `divide(divisor, 10, RoundingMode.HALF_UP)`.
4. Log statistics defensively: compute percentages only when the denominator is strictly positive (`if (denominator > 0)`).
5. In UIs, validate numeric fields before they reach service/calculation layers.

## Prevention

- Treat zero as a first-class edge case in every function that divides.
- Write property-based tests that include `0`, negative and extreme values.
- Use `Math.floorDiv` / a check to make intent obvious.
- Configure static analysis to flag `/` on variables not proven non-zero.

## Related Errors

- `NumberFormatException`
- `IllegalArgumentException`
- `NullPointerException`
- `ArgumentOutOfRange`-style errors in other languages