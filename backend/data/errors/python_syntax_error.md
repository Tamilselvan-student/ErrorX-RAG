---
error_name: SyntaxError
language: Python
category: Syntax Error
---

# SyntaxError

## Description

`SyntaxError` is raised by the Python *parser* when the source code is not valid
Python — it never even reaches execution. The message shows the reason and the
caret `^` points at the exact character. Common cases: missing colons, unmatched
braces/parentheses, invalid indentation (`IndentationError`, its subclass),
mismatched quotes, or using a keyword as a variable name.

## Common Causes

- Missing `:` after `def`, `if`, `for`, `while`, `class`, `try`/`except`/`else`/`finally`, `with`.
- Unbalanced parentheses, brackets, or quotes — often invisible in an editor until a linter complains.
- Mixing tabs and spaces for indentation, or inconsistent indentation depth (`IndentationError: unexpected indent`).
- Using reserved words as names (`class`, `lambda`, `None`) or forgetting the `f` in an `f-string`.
- Copy-pasting code edited in a word processor (smart quotes `''` instead of `'`).
- A stray line `def foo();` (semicolon) — semicolons are legal after a simple statement but not after `def`.

## Example

```python
def greet(name)      # BAD: missing colon
    print("Hi", name)

greet("Ada")
```

Fixed version:

```python
def greet(name):     # GOOD: colon after the signature
    print("Hi", name)

greet("Ada")
```

Unbalanced:

```python
data = {"name": "Ada",   # BAD: closing } missing → SyntaxError: unexpected EOF
```

## Why It Happens

Python compiles source to bytecode before running anything. The *parser* validates
the whole file against the grammar; the moment a token sequence does not fit, it
stops with `SyntaxError` and points at the failure. Because parsing precedes
execution, even "harmless" syntax mistakes in a function you never call will crash
the whole module import.

## Solutions

1. Read the caret line — the `^` marks the token where parsing failed, often one token *after* the actual mistake.
2. Check the line above the caret for missing colons, braces, or brackets.
3. Indentation: keep a 4-space policy, and let your editor *convert tabs to spaces*.
4. Suspect invisible characters: paste through a hex view, or retype the offending line.
5. When it says `unexpected EOF while parsing`, you are missing a closing bracket/quote somewhere above.
6. Run `python -m py_compile file.py` to syntax-check without executing.

## Prevention

- Configure the formatter (`black`/`ruff format`) in CI so formatting drift fails fast.
- Enable the editor's bracket-match highlighting and linter.
- Keep files short and consistent (one style).
- Pre-commit hooks (`ruff`, `pre-commit`) catch these on every commit.

## Related Errors

- `IndentationError`
- `NameError`
- `TabError`
- `SyntaxError` (JavaScript)