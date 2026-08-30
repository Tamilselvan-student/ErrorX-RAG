---
error_name: ClassCastException
language: Java
category: Runtime Error
---

# ClassCastException

## Description

`ClassCastException` is thrown when the JVM cannot convert an object reference to
the type you asked for, e.g. `(String) value` where `value` is actually an
`Integer`. Java is mostly statically typed, so this error almost always comes from
code that deliberately casts to a more specific type at runtime — typically after
reading from untyped containers, deserializing JSON/XML, or switching on `instanceof`.

## Common Causes

- Casting an item from a *raw* `List`/`Map` to a concrete type without knowing its actual class.
- Unchecked casts from generic collections: `List<String>` at runtime is really `List<Object>`.
- Serialization/deserialization mapping errors (Jackson/Gson producing a `Map` or a different type than the field expects).
- Implementing `equals`/`compareTo` across incompatible types.
- Wrong interface implementation passed into a method that casts to a specific class.

## Example

```java
Object value = Integer.valueOf(42);

String text = (String) value;  // BAD: throws ClassCastException at runtime
```

Fixed version:

```java
Object value = Integer.valueOf(42);

if (value instanceof String s) {
    System.out.println(s);
} else {
    // handle the unexpected type explicitly
    System.out.println("Expected a String but got " + value.getClass().getSimpleName());
}
```

## Why It Happens

Every object in the JVM knows its actual class. A cast is only a *compile-time*
assertion; the JVM checks at runtime whether the target type is assignable from
the object's real class. If not, the check fails and the JVM throws before the
object is ever treated as the wrong type — which preserves memory safety.

## Solutions

1. Inspect the stack trace: the frame with the cast (`(Type) ...`) is the culprit.
2. Prefer `instanceof`-checked casts to blind casts — Java 16+ supports pattern matching (`if (x instanceof String s)`).
3. When possible, avoid casts entirely: use properly parameterized generics and typed DTOs.
4. For deserialized data, validate the type at the boundary (e.g. Jackson `@JsonTypeInfo`, or explicit `readValue(..., TargetClass.class)`).
5. When reading mixed-type data, branch on `getClass()` / `instanceof` for each known shape.

## Prevention

- Never use raw types: `List<String> items = new ArrayList<>();` not `List items = ...`.
- Keep casts close to the data source so the mistake is easy to see.
- Unit-test deserialization with the worst-case payloads your API can receive.
- Enable warnings (`-Xlint:unchecked`) and treat them as errors in CI.

## Related Errors

- `NullPointerException`
- `IllegalArgumentException`
- `ClassNotFoundException`
- `NoClassDefFoundError`