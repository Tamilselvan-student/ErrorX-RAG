---
error_name: IndexError
language: Python
category: Runtime Error
---

# IndexError

## Description

`IndexError` is raised when you index a sequence (list, tuple, string, bytes) with
a position outside its bounds — `items[len(items)]` when the last valid index is
`len(items) - 1`. The message tells you the index: `IndexError: list index out of
range`. It is a `LookupError`, like `KeyError` (which plays the same role for
mappings).

## Common Causes

- Reading `args[0]` from a CLI program invoked without arguments.
- An off-by-one in a loop that collects/generates items (`result[i]` after `i` reached the length).
- Accessing position `len(data)` on an *empty* list (the classic `text[0]` on `""`).
- Parsing log/CSV lines with fewer fields than your code assumes.
- Assuming at least one element exists (e.g. after `data.split(",")`).
- Confusing `list.pop()` (last element) with `list.pop(0)` when the list is empty.

## Example

```python
lines = load_config_lines()          # returns [] in this run
first = lines[0]                     # BAD: IndexError: list index out of range
```

Fixed version:

```python
lines = load_config_lines()

if not lines:
    print("Config file is empty — using defaults")
    first = "DEFAULT"
else:
    first = lines[0]
```

## Why It Happens

Sequences are ordered containers with a length. Python stores the length and every
subscript is checked against it. When the requested offset is negative in the wrong
way or past the end, there is no element to return, so Python raises `IndexError`
instead of fabricating data. The root cause is usually an assumption about the
minimum length/contents of the sequence.

## Solutions

1. Read the message; `list index out of range` means the container had fewer elements than your index assumed.
2. Guard with `if len(seq) > idx:` before access, or use `min(idx, len(seq) - 1)` when a nearest-neighbor is fine.
3. For empty-or-default patterns use `seq[0] if seq else default`.
4. Favor iteration (`for item in seq`) over indexed access when you do not need random access.
5. Validate parsed input (splitting, regex groups, CSV rows) before indexing those results.
6. Replace `pop()` on possibly-empty collections with a guarded helper.

## Prevention

- Program against collections with iteration and slicing instead of positional subscripts where possible.
- Add `assert` / validation of expected length at data boundaries.
- Unit-test the empty, single-item, and many-item cases of every parser.
- Use `np.take`/`min` windowing helpers in numerical code that translates indices.

## Related Errors

- `KeyError`
- `StopIteration`
- `TypeError`
- `ArrayIndexOutOfBoundsException` (Java)