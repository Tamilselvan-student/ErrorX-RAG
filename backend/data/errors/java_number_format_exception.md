---
error_name: NumberFormatException
language: Java
category: Runtime Error
---

# NumberFormatException

## Description

`NumberFormatException` is thrown when a `String` cannot be converted into a
number by methods such as `Integer.parseInt`, `Long.parseLong`,
`Double.parseDouble`, or when an object string is passed to a wrapper like
`new BigDecimal(text)`. It is a subclass of `IllegalArgumentException`. The
message shows the offending input, e.g. `For input string: "abc"`.

## Common Causes

- Parsing user input, config values, or query parameters without validation.
- Locale-related formatting: `"1.5"` fails `Integer.parseInt` and `"3,14"` fails `Double.parseDouble` because of comma vs dot decimals.
- Leading/trailing whitespace or invisible characters (BOM, non-breaking space).
- Empty string `""` passed to a parse method.
- Trimming omitted: `" 42 "` fails on older JDKs; `"42 "` is tolerated in some APIs, `" 42"` is not consistent across versions.
- Wrong type in the payload (e.g. JSON sends `"1800x"` for a price).

## Example

```java
String input = "42x";
int value = Integer.parseInt(input);   // BAD: NumberFormatException: For input string: "42x"
```

Fixed version:

```java
String input = "42x";
try {
    int value = Integer.parseInt(input.trim());
    System.out.println(value);
} catch (NumberFormatException e) {
    System.out.println("Invalid number: '" + input + "' — ask for input again.");
}
```

## Why It Happens

Number conversion must scan every character and decide whether the whole string is
a syntactically valid number literal. As soon as one character does not fit
(digits, optional sign, optional decimal point, optional exponent), the parse
cannot produce a value, and throwing an exception is the only safe way to signal
that failure. Return codes were judged too easy to ignore.

## Solutions

1. Read the message: `For input string: "..."` shows the exact offending text, often revealing hidden whitespace or a bad separator.
2. Sanitize before parsing: `text.trim()`, remove grouping characters, check `text.isEmpty()` first.
3. Use a parsing helper wrapped in try/catch with a friendly fallback instead of letting the exception bubble up.
4. For decimals, use `BigDecimal` / `NumberFormat` with an explicit `Locale` (e.g. `Locale.ROOT`).
5. Prefer framework-provided type binding (e.g. `@RequestParam int`, JSON deserializers) that centralizes errors.

## Prevention

- Validate input format with a regex or a dedicated parser before numeric conversion.
- Set the locale explicitly in all formatting/parsing code (`DecimalFormatSymbols` with `Locale.ROOT`).
- Have a single, well-tested method to parse numbers in your application.
- Add unit tests for edge strings: `""`, `"  "`, `"1,5"`, `"0x10"`, `"1e999"`.

## Related Errors

- `IllegalArgumentException`
- `ArithmeticException`
- `NullPointerException`
- SQL type mismatch errors