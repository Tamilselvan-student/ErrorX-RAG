---
error_name: FileNotFoundException
language: Java
category: IO Error
---

# FileNotFoundException

## Description

`FileNotFoundException` is a checked `IOException` thrown when Java cannot open a
file at the given path — the path does not exist, points to a directory where a
file is expected, or the process lacks read permissions. Because it is checked,
the compiler forces you to declare or catch it, but the *path bug* usually only
shows up at runtime.

## Common Causes

- A relative path that depends on the current working directory (which differs between IDE and production).
- The file genuinely does not exist (wrong filename, wrong folder, typo).
- The file exists but the process has no read permission (config paths, CI sandboxes, Docker containers).
- Paths built from `\` vs `/` or containing env vars that are empty.
- On Windows, parsing a raw path as `URI` incorrectly (`src/conf.properties` vs `file:/...`).
- Using `ClassLoader.getResource` but pointing at a directory instead of a resource file.

## Example

```java
File config = new File("config.properties");       // depends on CWD
BufferedReader reader = new BufferedReader(new FileReader(config)); // BAD: may throw FileNotFoundException
```

Fixed version (resolves relative to the classpath resource):

```java
try (InputStream in = App.class.getResourceAsStream("/config.properties")) {
    if (in == null) {
        throw new IllegalStateException("config.properties not on classpath");
    }
    // ... read from in
}
```

## Why It Happens

The OS reports to the JVM that the file cannot be opened. Java wraps that OS-level
result in `FileNotFoundException` carrying the *resolved* path. In most projects
the real cause is a mismatch between the path you believe you are opening and the
physical path the JVM actually resolves (working directory differs from your IDE
view, or resource files are not copied to the build output).

## Solutions

1. Print/log `file.getAbsolutePath()` to confirm the resolved location.
2. Prefer classpath resources (`ClassLoader.getResource` / `getResourceAsStream`) for bundled files.
3. Verify the resource appears in the build output (`target/classes` or `build/resources`) — most IDEs re-copy it, but a clean build often reveals stale resources.
4. Load file names from configuration, never from string concatenation of paths.
5. Check `file.exists()`, `file.canRead()` and print a descriptive error before opening.
6. In Docker/CI, mount/verify the expected directory and its permissions explicitly.

## Prevention

- Keep configuration relative to a well-defined base (project root or classpath), not the CWD.
- Add a startup check that fails fast with a clear message when required files are missing.
- Treat file access as I/O with explicit error handling and never swallow it silently.
- Store golden-path tests that read the exact resources your code reads.

## Related Errors

- `IOException`
- `NoClassDefFoundError`
- `ClassNotFoundException`
- `IllegalArgumentException` (from malformed path URIs)