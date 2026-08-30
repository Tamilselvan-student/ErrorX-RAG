---
error_name: FileNotFoundError
language: Python
category: IO Error
---

# FileNotFoundError

## Description

`FileNotFoundError` is a subclass of `OSError` raised when an `open()` (or
`Path.read_text()`/`read_bytes()`, `os.remove`, `shutil`, ...) targets a file or
directory that does not exist. The message includes the offending path:
`[Errno 2] No such file or directory: 'missing.txt'`.

## Common Causes

- The relative path does not exist relative to the *current working directory* (which changes between the IDE, tests, and cron/systemd).
- The file is generated at a different stage (a data file created after the script ran, or only in another environment).
- A typo in the filename, or an extension mismatch (`config.yaml` vs `config.yml`).
- Missing parent directory — `open('logs/app.log', 'w')` fails because `logs/` does not exist yet.
- A symlink that points to a non-existent target.
- Running in a container/CI without the expected volume mounted.

## Example

```python
with open("data/report.json", "r") as f:    # BAD: FileNotFoundError if path missing
    payload = f.read()
```

Debug and fix:

```python
import os
from pathlib import Path

target = Path.cwd() / "data" / "report.json"
if not target.exists():
    print(f"Missing data file at {target} — run generate_data.py first")
    raise SystemExit(1)

with open(target, "r", encoding="utf-8") as f:
    payload = f.read()
```

## Why It Happens

Python asks the operating system to open the path; the OS answers `ENOENT`. The
path Python sends is the literal string that you resolved from the current working
directory — so when the file "works" in your editor but fails in CI, the working
directory difference is the usual suspect.

## Solutions

1. Print the absolute path (`Path(p).resolve()`) to see exactly what the OS received.
2. Create parent directories before writing: `Path(path).parent.mkdir(parents=True, exist_ok=True)`.
3. For packaged resources, use `importlib.resources` instead of guessing relative paths.
4. Check existence with a clear branch, and produce an actionable message when missing.
5. Make paths environment/config-driven, resolved against a stable base at startup.
6. In tests, isolate with `tmp_path` and never depend on random CWDs.

## Prevention

- Bootstrap scripts that generate expected files at the start of the pipeline.
- Centralize path resolution in one config module; verify all required paths at startup.
- Pin working directory (`os.chdir`) or use absolute paths in scheduled jobs.
- Add a golden integration test that creates + reads the exact files production uses.

## Related Errors

- `PermissionError` (same family, different cause)
- `IsADirectoryError`
- `FileNotFoundException` (Java)
- `OSError`