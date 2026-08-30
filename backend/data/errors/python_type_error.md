---
error_name: TypeError
language: Python
category: Runtime Error
---

# TypeError

## Description

`TypeError` is raised when an operation or function is applied to a value of an
inappropriate type — for example concatenating a string with an integer, calling
an object that is not callable, or passing the wrong number/kind of arguments.
Python is dynamically typed, so these mistakes surface at runtime, exactly where
the incompatible value flows in.

Typical messages: `unsupported operand type(s) for +: 'int' and 'str'`,
`'NoneType' object is not subscriptable`, `missing 1 required positional argument`.

## Common Causes

- Mixing types in expressions: `"count: " + count` where `count` is an `int`.
- Calling `None`, e.g. a function that forgot its `return` yields `None` and the caller immediately invokes `.method()` on it.
- Using `range()` or indexing where the object is a dict or a `None`.
- Passing the wrong argument types to library functions (a `str` where an `int` was expected).
- Missing/extra `*args` or keyword-only parameters.
- Iterating over an integer (`for x in 42`). 
- Boolean/int confusion with operators like `+` on `bool` flows.

## Example

```python
name = "Ada"
age = 37

# BAD: str + int is not allowed
message = "User " + name + " is " + age + " years old"
```

Fixed version:

```python
name = "Ada"
age = 37

message = f"User {name} is {age} years old"
```

Another classic — the None-returning function:

```python
def fetch_user(user_id):
    if user_id < 1:
        return None          # caller expects an object
    return {"name": "Ada"}

profile = fetch_user(0)
print(profile["name"])       # BAD: TypeError: 'NoneType' object is not subscriptable
```

## Why It Happens

Python checks types *when the operation runs*. Operators dispatch to methods on the
objects involved (`__add__`, `__getitem__`, ...). When the target method is missing
or the types are incompatible, Python raises `TypeError` instead of guessing. The
message names the types involved, which usually makes the offending variable obvious.

## Solutions

1. Read the message — it almost always names both types (e.g. `'int' and 'str'`), so find the variable whose type is unexpected.
2. Add a debugging print/repr or use a debugger to inspect the actual types at the failing line.
3. Cast deliberately when needed: `str(count)`, `int(value)` (guarded by try/except), `list(items)`.
4. If a library call fails, verify the documented argument types instead of guessing.
5. When you see `'NoneType' object is not ...`, trace the function that returned `None` and handle that branch explicitly.
6. Enable a type checker (mypy/pyright) — it catches most of these before they run.

## Prevention

- Type-annotate public functions and run `mypy` in CI.
- Use `f-strings` instead of manual `+` concatenation.
- Return explicit error values or raise from a helper rather than returning bare `None` from functions others call.
- Treat functions that legitimately return `None` as "maybe" (`Optional[T]`) and check before use.

## Related Errors

- `AttributeError`
- `ValueError`
- `NameError`
- `TypeError` in JavaScript