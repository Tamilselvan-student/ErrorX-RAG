---
error_name: NullPointerException
language: Java
category: Runtime Error
---

# NullPointerException

## Description

`NullPointerException` (NPE) is thrown when your code tries to use an object
reference that holds the value `null` — for example, calling a method on it,
reading a field from it, or using it as an array/target of a synchronized block.
It is a `RuntimeException`, so the compiler will not warn you about it; it only
appears at the moment your code runs along the offending branch.

A typical message looks like:

`java.lang.NullPointerException: Cannot invoke "User.getName()" because "user" is null`

## Common Causes

- Dereferencing a method/local variable that was never initialized (default `null`).
- Calling a method on the result of a lookup that returned nothing (e.g. a map, a
  repository, a factory) without null-checking it.
- Storing `null` in a collection/array and later reading it back.
- Assigning an object in the constructor but using the field before assignment.
- Chained calls such as `order.getCustomer().getAddress()` where an intermediate
  object is `null`.
- UI/DI frameworks returning `null` for an unregistered component or bean.

## Example

```java
public class UserService {
    public String greet(User user) {
        // BAD: crashes with NullPointerException when user is null
        return "Hello " + user.getName().toUpperCase();
    }
}
```

Fixed version:

```java
public class UserService {
    public String greet(User user) {
        if (user == null) {
            return "Hello, anonymous user";
        }
        String name = user.getName();
        return "Hello " + (name != null ? name.toUpperCase() : "friend");
    }
}
```

## Why It Happens

In Java an *object variable* is really a reference. `null` means "this reference
points to nothing". When you write `user.getName()`, the JVM first loads the
`user` reference, finds it points to `null`, and cannot follow it — so it throws
instead of silently doing something undefined (a design decision Java copied
responsibly). The message often includes *exactly* which reference is null and
which call triggered it.

## Solutions

1. Read the full stack trace — the first frame in *your* code is where the dereference happened.
2. Find which variable is `null` (the exception message usually names it) and add a guard.
3. Use `Objects.requireNonNull(x, "x must be provided")` for parameters that must never be null — fail fast at the boundary.
4. For optional lookups use `java.util.Optional` or at least an explicit null check.
5. Initialize collections (`new ArrayList<>(...)`) instead of leaving fields `null`.
6. In tests, reproduce the failing path and assert on the guard behavior.

## Prevention

- Annotate the contract with `@Nullable` / `@NonNull` (JSpecify) and run a static analyzer such as Error Prone or SpotBugs.
- Never return `null` from methods when an empty collection or `Optional` communicates intent better.
- Check inputs once at the method boundary, not deep inside the logic.
- Avoid deep call chains like `a.getB().getC().do()` unless every link is guaranteed non-null.

## Related Errors

- `ClassCastException`
- `IllegalArgumentException`
- `NoSuchElementException`
- `NullPointerException` in JavaScript (``Cannot read properties of null``)