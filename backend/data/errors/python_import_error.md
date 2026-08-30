---
error_name: ImportError
language: Python
category: Module Loading Error
---

# ImportError

## Description

`ImportError` is raised when an `import` statement or `from x import y` cannot
satisfy the request — the module is missing, the name is not defined in it, or the
module itself fails to load. `ModuleNotFoundError` (its subclass) is the specific
case where the module cannot be found anywhere on `sys.path`.

Typical messages: `No module named 'requests'`,
`cannot import name 'foo' from 'bar'`, `ImportError: attempted relative import`.

## Common Causes

- A dependency is not installed in the active environment (`pip install ...` into a different venv, or never installed).
- Running from the wrong working directory so `sys.path[0]` misses the project root.
- `sys.path` does not contain the directory of the module (running a script from `tests/` that imports `app`).
- The module exists but imports a sibling that itself crashes (the real error is wrapped).
- Circular imports: module A imports B which imports A.
- Relative imports without a package context: `from . import foo` inside a script run directly.
- Typos: `import requets` vs `requests`; or importing an object actually defined elsewhere.

## Example

```python
# BAD: package not installed in the active environment
import numpy_extra_thing
data = numpy_extra_thing.load()
```

```bash
# Fix: install the package (verify the environment first!)
pip install numpy-extra-thing
```

```python
# BAD: circular import — utils imports db, db imports utils
# utils.py
from db import get_conn
```

Fixed approach — move the shared dependency to a lower-level module or import lazily:

```python
# utils.py — import inside the function, no top-level cycle
def get_conn():
    from db import get_conn  # deferred import breaks the cycle
    return get_conn()
```

## Why It Happens

`import` executes the module code and registers its names. Python walks `sys.path`
in order for `import X`; if the module is found at none of the entries, or the
`from ... import name` name is absent after execution, it raises. When the module
file exists but throws during its own top-level code, the import raises too — and
the original exception is often visible in the traceback above the import line.

## Solutions

1. Read the message first: `No module named X` → dependency problem; `cannot import name Y` → name/path problem; `attempted relative import` → package/run-mode problem.
2. Check the active environment: `pip list`, `python -c "import sys; print(sys.executable)"` — you may be using a different interpreter than the one you installed into.
3. Print `sys.path` and confirm the project root is there; run with `python -m package.module` instead of a bare script path.
4. Resolve circular imports by moving shared code to a third module or importing lazily inside functions.
5. Name the specific thing: prefer `from module import Class` and correct the typos by inspecting the module (`dir(module)`).
6. For relative imports, keep scripts as modules inside a package and run them with `-m`.

## Prevention

- Pin dependencies in `requirements.txt`/`pyproject.toml` and use one virtualenv per project.
- Structure packages with a clear dependency direction (no cycles in the import graph).
- Use explicit imports and give modules unique names that do not shadow stdlib/packages.
- CI should recreate the environment from lock files and run the app the same way it runs in production.

## Related Errors

- `ModuleNotFoundError`
- `AttributeError` (on a partially imported module)
- `NameError`
- `ClassNotFoundException` (Java, analogous miss)