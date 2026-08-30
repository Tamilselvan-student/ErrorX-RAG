---
error_name: NameError
language: Python
category: Runtime Error
---

# NameError

## Description

`NameError` is raised when code uses a name that Python cannot resolve — a
variable, function, class, or imported name that has not been defined (or has
fallen out of scope) at that point. The classic message is
`NameError: name 'foo' is not defined`, which names the exact offending identifier.

## Common Causes

- Typos that look plausible: `userName` vs `username`, `self.setup` vs `self.setUp`.
- Using a variable before it is assigned on some code path (assignment inside an `if` that did not run).
- Forgetting to import a function: using `random.choice(...)` without `import random`.
- Name shadowing: a local variable shadows a function defined later/elsewhere.
- Referring to a variable from an enclosing scope that is actually local (often due to assignment in the function).
- Using a name from another module's namespace directly instead of via `module.name`.

## Example

```python
def greet(user):
    greeting = f"Hello {user_name}"   # BAD: NameError: name 'user_name' is not defined
    return greeting
```

Should read:

```python
def greet(user):
    greeting = f"Hello {user}"        # GOOD: uses the actual parameter
    return greeting
```

Another scenario — branch-dependent assignment:

```python
enabled = is_feature_on()
if enabled:
    banner = "New UI"
print(banner)      # BAD: NameError if enabled was False (banner never assigned)
```

## Why It Happens

Python resolves names at runtime using a well-defined scope order: local, enclosing,
global, builtins. When a name is read and none of these scopes contains it, there
is nothing to load, so Python raises `NameError` naming the identifier. This is
Python's dynamic nature: it does not pre-declare variables, so "not defined yet" is
the only possible source of the value.

## Solutions

1. Search the traceback for the exact name in the message, then find where it *should* be defined.
2. Initialize variables before any branch that uses them (e.g. `banner = None` before the `if`).
3. Check for typo drift between definition and use (search both spellings).
4. Verify imports: `import random` / `from random import choice` either prefix or import the exact name.
5. When a variable is expected from a function, confirm it is `return`ed (not just printed) and caught.
6. Use a debugger to break at the failing line and inspect the namespace.

## Prevention

- Keep function locals short-lived and close to their use site.
- Configure static checkers (Pyflakes/ruff) — they flag undefined names and unused typos immediately.
- Add type annotations; implicit `Any` hides NameError-prone code.
- Refactor long functions so names cannot be accidentally shared or shadowed.

## Related Errors

- `AttributeError`
- `ImportError`
- `UnboundLocalError` (its cousin)
- `ReferenceError` (JavaScript)