---
error_name: AttributeError
language: Python
category: Runtime Error
---

# AttributeError

## Description

`AttributeError` is raised when you access an attribute or method that an object
does not have: `user.name` when the object is a `dict` (use `user["name"]`), or
`items.length` when the attribute is spelled `items.len` through a helper, or
calling a method when the thing is `None`. The message names the attribute:
`'NoneType' object has no attribute 'name'`.

## Common Causes

- Reading a `dict` with attribute syntax: `data.name` instead of `data["name"]`.
- Calling methods on the result of a function that returned `None` (`.strip()`, `.append()`, `.lower()` chains).
- Misspelled attribute names (`self.userName` vs `self.username`, `.UPPERCASE()`).
- Importing the wrong class; the object is a different type than you assumed.
- Modules/objects that dropped an attribute after an upgrade or a rename.
- Accessing `__init__` fields before `super().__init__` runs.

## Example

```python
data = {"name": "Ada", "age": 37}
print(data.name)          # BAD: AttributeError: 'dict' object has no attribute 'name'
```

Correct syntax:

```python
print(data["name"])       # GOOD: dicts are subscripted, not attribute-accessed
```

The None follow-on:

```python
text = fetch_message()    # returns None in some cases
print(text.upper())       # BAD: AttributeError: 'NoneType' object has no attribute 'upper'
```

## Why It Happens

Python objects store attributes in their own namespace plus their class's
`__dict__`/`__slots__`. `getattr(obj, name)` resolves the name; if neither the
object nor its class defines it, Python raises `AttributeError`. The common root
cause is an assumption about what type the object actually is (a `dict` has keys,
not attributes — and `None` has nothing at all).

## Solutions

1. Check the message: `'dict' object has no attribute 'x'` means use `obj["x"]`; `'NoneType' object has no attribute 'x'` means something returned `None`.
2. Use `getattr(obj, name, default)` when the attribute is optional and you have a sensible fallback.
3. Guard `None` results: `if result is not None:` before chaining, or return a real default object.
4. Verify the object's type with `type(obj)`, `isinstance`, or a debugger at the failing line.
5. When using plain data, access via `Mapping` methods, not attribute syntax.
6. Fix chained calls that can collapse on `None`: `obj.x.y` → validate `obj.x` first.

## Prevention

- Use dataclasses/pydantic models for structured data so fields are real attributes.
- Annotate return types (`Optional[T]`), and do not annotate `-> None` planning to return a value afterwards.
- Run a type checker in CI — it catches attribute typos and `None`-chain risks.
- Keep public attribute names in one place (constants/slots) to prevent drift.

## Related Errors

- `NameError`
- `KeyError`
- `TypeError`
- `UnboundLocalError`