---
error_name: IllegalArgumentException
language: Java
category: Runtime Error
---

# IllegalArgumentException

## Description

`IllegalArgumentException` is thrown when a method receives an argument that is
formally well-typed but semantically invalid — a negative size, an `enum` value
outside the supported set, an empty collection where a non-empty one is required.
Libraries throw it to fail fast when their contract is violated. The message
usually explains the constraint, e.g. `Size must be positive`.

## Common Causes

- Passing a negative or zero value where positive is required (sizes, counts, intervals).
- Passing `null` where the contract forbids it (although older APIs use `NullPointerException` here).
- Passing an out-of-range index, an unknown enum constant, or an integer that is too large for the operation.
- Misuse of a framework method — e.g. giving `Arrays.copyOfRange` a `from > to`.
- Supplying a format/pattern string to `DateTimeFormatter`, `MessageFormat` or regex APIs that fails their grammar.

## Example

```java
public void createAccount(String email, int minPasswordLength) {
    if (minPasswordLength < 8) {
        throw new IllegalArgumentException(
            "minPasswordLength must be at least 8, got " + minPasswordLength
        );
    }
    // ...
}
// call site
createAccount("alice@example.com", -1);  // BAD: IllegalArgumentException
```

## Why It Happens

Java's type system checks *what kind* of value is passed (`int`, `String`) but not
*which* values are meaningful for a given operation. `IllegalArgumentException` is
the standard runtime signal that a method's documented precondition was violated —
it surfaces the mistake close to the source instead of letting bad data corrupt
state several calls later.

## Solutions

1. Read the stack trace: the exception is usually thrown *inside* the library call; the first frame in *your* code shows the offending argument.
2. Validate arguments at every public API boundary with explicit checks, then `throw new IllegalArgumentException("...")` with a descriptive message.
3. Use Java 8+ `Objects.requireNonNull` for nulls, and `Preconditions` (Guava) if you adopt it.
4. Normalize input early (trim strings, clamp numbers) before it reaches library calls.
5. Test the boundary values that your contract names (min, max, just-outside).

## Prevention

- Document preconditions with `@throws IllegalArgumentException` in Javadoc.
- A single `private static void checkPositive(int v, String name)` style helper removes repetition.
- Centralize argument validation for DTOs (Bean Validation `@Min`, `@NotBlank`).
- Add fuzz/property tests that throw random values at public methods.

## Related Errors

- `NumberFormatException` (subclass)
- `NullPointerException`
- `IndexOutOfBoundsException`
- `IllegalStateException`