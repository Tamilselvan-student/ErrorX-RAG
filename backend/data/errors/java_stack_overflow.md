---
error_name: StackOverflowError
language: Java
category: JVM Error
---

# StackOverflowError

## Description

`StackOverflowError` is thrown when a thread's call stack grows beyond the JVM's
reserved stack size — almost always because recursion never reaches its base case
(or each call consumes more stack than the default allowance). It is an `Error`,
not an `Exception`, and the message is typically just `null`. The stack trace is
normally a long repeating sequence of the same few frames.

## Common Causes

- Missing or unreachable base case in recursion (e.g. `factorial(n) { return n * factorial(n) }`).
- Indirection loops: `a()` calls `b()` which calls `a()` with no terminating condition.
- Deep but legitimate recursion on large inputs (tree traversal, JSON/XML parsing of a deeply nested document).
- Accidentally calling a method on the instance from inside itself (e.g. `equals` calling `this.equals(...)`).
- Jackson/Moshi-style recursive serialization of bidirectional object graphs.
- Testing recursion on inputs larger than the default thread stack.

## Example

```java
public class Recursive {

    public static long factorial(int n) {   // BAD: no base case for n < 1
        return n * factorial(n - 1);        // runs forever → StackOverflowError
    }

    public static void main(String[] args) {
        System.out.println(factorial(5));
    }
}
```

Fixed version:

```java
public static long factorial(int n) {
    if (n <= 1) {           // base case terminates the recursion
        return 1L;
    }
    return n * factorial(n - 1);
}
```

## Why It Happens

Every method invocation pushes a new stack frame (local variables, return address,
intermediate state). The JVM reserves a fixed stack region per thread (typically
512 KB–1 MB). Deep recursion consumes frame after frame until there is no room; at
that point the next call cannot proceed, and the JVM aborts that thread's stack
growth with `StackOverflowError`.

## Solutions

1. Confirm the recursion: the repeated frames in the trace reveal the cycle.
2. Add/verify the base case and make sure every recursive branch moves toward it.
3. Convert recursion to iteration (`for`/`while` + explicit stack) for work proportional to input size.
4. For known deep-but-finite recursion (parsing), either increase `-Xss` for that thread or switch to an iterative parser.
5. Break recursive object graphs: mark bidirectional fields with `@JsonIgnore`/skip references before serialization.
6. Run a quick smoke test with the maximum realistic input to prove it terminates.

## Prevention

- Prefer iterative algorithms for linear work; reserve recursion for naturally logarithmic depth.
- Add explicit depth counters in recursive helper methods and fail fast past a sane limit.
- Unit-test recursion against large and hostile inputs (including a self-referencing object graph).
- Load-test serialization of real payloads, not just happy-path examples.

## Related Errors

- `OutOfMemoryError`
- `RecursionError` (Python)
- `Maximum call stack size exceeded` (JavaScript)
- `IllegalStateException`