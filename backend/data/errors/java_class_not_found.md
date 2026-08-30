---
error_name: ClassNotFoundException
language: Java
category: Class Loading Error
---

# ClassNotFoundException

## Description

`ClassNotFoundException` is thrown when the JVM cannot locate a class by name via
reflection (`Class.forName(...)`) or when a classloader cannot load a class the
code explicitly asked for. It is a *checked* exception. Its relative,
`NoClassDefFoundError`, is thrown when a class was available at compile time but is
missing/deformed at run time.

## Common Causes

- Missing dependency at runtime that was present at compile time (scope issues, deployment server without provided JARs).
- Wrong artifact in the build (snapshot is absent from the local repository, shaded jar dropped the class).
- The class name passed to `Class.forName` is misspelled or includes the wrong package.
- Driver/service classes inside fat-JARs that use SPI manifests not merged correctly.
- Multiple versions of a JAR on the classpath (version conflict) hiding the class.

## Example

```java
Class<?> driver = Class.forName("com.example.MyDatabaseDriver");
// BAD: throws ClassNotFoundException if the driver class is not on the classpath
```

Robust variant:

```java
try {
    Class.forName("com.example.MyDatabaseDriver");
} catch (ClassNotFoundException e) {
    log.error("Driver class is missing. Add the dependency or fix the name.", e);
    throw new IllegalStateException("Database driver not available", e);
}
```

## Why It Happens

Java resolves classes lazily — at the moment of first use. Reflection calls such as
`Class.forName(...)` trigger that resolution immediately. When the target class is
not present in any classloader visible to the caller, the JVM cannot proceed and
throws, telling you exactly which class was missing from the classpath.

## Solutions

1. Note the missing class in the message and check the dependency that should provide it.
2. Verify the classpath: `mvn dependency:tree`, print classloader URLs, or inspect the FAT jar contents.
3. For `Class.forName`, double-check the fully qualified name (package `+` class), including spelling.
4. If it happens only in production, compare your deployable artifact vs. local run (missing runtime-scope JARs are the classic cause).
5. For JDBC/SPI drivers, ensure the service-loader entry (`META-INF/services`) survives packaging or register the driver explicitly.
6. Add a startup check that loads all driver classes eagerly so the failure is immediate and clear.

## Prevention

- Make dependency scope explicit and verify with an artifact-level test in CI.
- Keep one version of each library on the classpath (enforce with a BOM or dependency management).
- Use `getResourceAsStream`/`ServiceLoader` instead of raw `Class.forName` where the standard solves it.
- Print the effective classpath in verbose mode during integration debugging.

## Related Errors

- `NoClassDefFoundError`
- `NoSuchMethodError`
- `LinkageError`
- `FileNotFoundException`