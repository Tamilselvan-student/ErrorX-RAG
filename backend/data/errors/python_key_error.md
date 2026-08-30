---
error_name: KeyError
language: Python
category: Runtime Error
---

# KeyError

## Description

`KeyError` is raised when you access a `dict` (or `defaultdict`/`Mapping`) key that
does not exist, e.g. `user["settings"]` when `user` has no `"settings"` key. The
message quotes the missing key: `KeyError: 'settings'`. It is a subclass of
`LookupError` and happens only at runtime, because dict keys are looked up
dynamically.

## Common Causes

- Reading a key that may legitimately be absent (optional JSON/API fields, form input).
- Data shape drift: the dict came from parsed JSON/config and was renamed, removed, or is nested deeper than expected.
- Building keys with a value that differs from how they were written (case, trailing space).
- Using the result of `dict.keys()`/`items()` from one dict to read another.
- Typos in string keys (`user["Settings"]` vs `user["settings"]`).

## Example

```python
user_profile = {"name": "Ada", "email": "ada@example.com"}

theme = user_profile["settings"]["theme"]   # BAD: KeyError: 'settings'
```

Fixed version:

```python
user_profile = {"name": "Ada", "email": "ada@example.com"}

settings = user_profile.get("settings", {})
theme = settings.get("theme", "light")      # safe defaults instead of exceptions
```

Or fail fast with a clear message when the key *must* exist:

```python
if "settings" not in user_profile:
    raise ValueError("user_profile is missing the 'settings' section")
theme = user_profile["settings"]["theme"]
```

## Why It Happens

Dictionaries are hash tables: Python hashes the key you ask for, looks in the
table, and if the key is absent it cannot synthesize a value. `KeyError` is the
signal "this key is not there right now". The deeper cause is usually an
assumption that the data always contains that key — and the data disagreed.

## Solutions

1. Look at the quoted key in the message — that exact string is what's missing.
2. Prefer `dict.get(key, default)`, `setdefault`, or a `defaultdict` when absence is normal.
3. If the key must exist, validate the expected shape up front with a clear, actionable check.
4. For nested data use `collections.abc.Mapping` + safe traversal helpers, or `try/except KeyError` around the one lookup.
5. When loading JSON, compare the payload sample against your assumed schema (a quick `pprint` often reveals the rename).
6. Consider a strict DTO/`pydantic` model so missing fields surface with field names at the boundary.

## Prevention

- Define and validate schemas for external data (JSON Schema, pydantic) instead of hand-plumbing dicts.
- Keep key strings in constants so typos cannot diverge.
- Write tests that exercise payloads with missing/empty optional sections.
- Use `Mapping.get` in library-facing code so callers get defaults rather than crashes.

## Related Errors

- `IndexError`
- `AttributeError`
- `TypeError`
- `StopIteration`