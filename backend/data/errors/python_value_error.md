---
error_name: ValueError
language: Python
category: Runtime Error
---

# ValueError

## Description

`ValueError` is raised when a function receives an argument with the right type
but an inappropriate value — `int("abc")`, `float("1,5")`, `list.index(x)` when
`x` is absent, `math.sqrt(-1)`, or unpacking too few values
(`too many values to unpack (expected 2)`). It is Python's standard signal that
the *value* violates a precondition even though the *type* is fine.

## Common Causes

- Converting text to a number when the text is not a valid literal (`int("12abc")`).
- Lookup-by-value APIs: `list.index()`, `set.remove()`, `str.index()` on a missing value.
- Math domain errors: `math.log(0)`, `math.sqrt(-1)`.
- Tuple/dict unpacking mismatches: `a, b = [1, 2, 3]`.
- Passing an out-of-range integer to functions like `chr()`, `bytes([-1])`.
- Library contract violations (e.g. `datetime.fromisoformat` on a malformed string).

## Example

```python
raw = "42oops"
number = int(raw)          # BAD: ValueError: invalid literal for int() with base 10: '42oops'
```

Fixed version:

```python
raw = "42oops"
try:
    number = int(raw)
except ValueError:
    number = 0
    print(f"'{raw}' is not a valid integer; falling back to 0")
```

Also, unpacking:

```python
parts = line.split(",")         # maybe ["a"]
name, value = parts             # BAD: ValueError: not enough values to unpack
```

```python
parts = line.split(",")
if len(parts) != 2:
    raise ValueError(f"expected 2 fields, got {len(parts)} from {line!r}")
name, value = parts
```

## Why It Happens

Python APIs favor raising over returning a sentinel, and `ValueError` is the
generic contract exception for "the value does not fit the operation". An `int()`
conversion cannot produce an integer from `"42oops"`, `index()` cannot return a
position for an absent element, so the only honest result is an exception naming
the offending value.

## Solutions

1. The message almost always quotes the offending value — use it to find the source variable.
2. Wrap user/format-dependent conversions in `try/except ValueError` with a sensible fallback.
3. Check before lookup: `if x in lst:` before `lst.index(x)`, `if x in dict:` before `dict[x]`.
4. Validate unpackable shapes with an explicit length check and a descriptive error.
5. Normalize input (`strip()`, regex-validate) early to cut off bad values before they reach math/parse calls.
6. Reproduce with the exact bad value via a quick unit test.

## Prevention

- Parse untrusted strings with dedicated validators (regex, `pydantic` types) at the boundary.
- Prefer dict lookups with defaults over `.index()`-style positional hunting.
- Write tests that include malformed-but-typed inputs (`"  42"`, `"1e999"`, `"١٢"`).
- Choose `Literal`/`Enum`-typed parameters instead of accepting arbitrary ints.

## Related Errors

- `TypeError`
- `KeyError`
- `IndexError`
- `NumberFormatException` (Java)