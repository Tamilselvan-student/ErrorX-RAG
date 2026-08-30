---
error_name: ArrayIndexOutOfBoundsException
language: Java
category: Runtime Error
---

# ArrayIndexOutOfBoundsException

## Description

`ArrayIndexOutOfBoundsException` is thrown when a program tries to access an array
element with an index outside the valid range `0 .. length-1`. Java arrays are
zero-based, so the *last* valid index is always `array.length - 1`. This also
applies to raw `String` arrays and to `char[]` returned by methods. Strings raise
a subclass, `StringIndexOutOfBoundsException`, when you index outside the string's
character range.

## Common Causes

- Off-by-one loop errors: iterating `for (int i = 0; i <= list.length; i++)` instead of `i < length`.
- Using a computed index that can go negative or past the end (e.g. `i - 1` on the first iteration).
- Reading `args[0]` without checking that the program was invoked with arguments.
- Confusing `array.length` with a 1-based counter.
- Slicing/`substring` boundaries computed from wrong indices.

## Example

```java
int[] numbers = {10, 20, 30};

for (int i = 0; i <= numbers.length; i++) {   // BAD: i goes to 3, max valid is 2
    System.out.println(numbers[i]);            // crashes on i == 3
}
```

Fixed version:

```java
for (int i = 0; i < numbers.length; i++) {     // GOOD: i stops at 2
    System.out.println(numbers[i]);
}
```

## Why It Happens

Arrays are fixed-size, contiguous memory regions. The JVM stores the length and
validates every access at runtime. When `index < 0 || index >= length`, the index
points to memory outside the array, so the JVM refuses the access and throws
rather than letting the program read or write arbitrary memory (that is what the
out-of-bounds check is for).

## Solutions

1. Find the `...ArrayIndexOutOfBoundsException: Index N, Size M` message — it tells you the exact failing index and the current array length.
2. Fix loops to use `< length` (not `<=`) and re-check helper indices.
3. Before accessing a computed index, guard: `if (idx >= 0 && idx < arr.length)`.
4. For "search or default" use `Arrays.binarySearch` + a bounds check, or iterate with an enhanced `for`.
5. When parsing CLI args, verify `args.length` first and print usage.
6. Add `assert idx < list.size();` in internal code and enable assertions while testing.

## Prevention

- Prefer enhanced `for-each` loops or streams when you do not need the index.
- Centralize index arithmetic in a tiny helper to avoid repeating off-by-one math.
- Build lists with `ArrayList` and use `get(i)` only inside `for (int i = 0; i < list.size(); i++)`.
- Add regression tests around min/max/empty collection boundaries.

## Related Errors

- `StringIndexOutOfBoundsException`
- `IndexOutOfBoundsException` (for `List`)
- `NegativeArraySizeException`
- `NoSuchElementException`