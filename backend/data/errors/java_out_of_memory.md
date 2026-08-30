---
error_name: OutOfMemoryError
language: Java
category: JVM Error
---

# OutOfMemoryError

## Description

`OutOfMemoryError` is thrown when the JVM runs out of memory in the heap (or,
depending on the subtype in the message, metaspace or direct memory) and repeated
garbage collection cannot reclaim enough. Common message suffixes:
`Java heap space`, `GC overhead limit exceeded`, `Metaspace`, or
`unable to create new native thread`. It is an `Error`, not something the code is
expected to catch and continue from.

## Common Causes

- A data structure that grows without bounds (a `List`/`Map` appended to in a loop, an unbounded cache).
- Loading an entire file/DB result set into memory instead of streaming.
- Memory leak via un-released references (e.g. storing objects in a `static` map, event listeners never removed).
- `OutOfMemoryError: Metaspace` from repeated class generation (dynamic proxies, nonstop codegen, hot-reload).
- Asking for too large an array/`StringBuilder` relative to heap.
- Not enough heap configured for the workload (`-Xmx` too low).

## Example

```java
public static void main(String[] args) {
    List<byte[]> buffers = new ArrayList<>();
    while (true) {
        buffers.add(new byte[1024 * 1024]);   // BAD: unbounded growth
    }
}
```

Fixed version example — bound the container and release references:

```java
public static void main(String[] args) {
    int maxBuffers = 50;
    ArrayDeque<byte[]> buffers = new ArrayDeque<>(maxBuffers);
    for (int i = 0; i < 1000; i++) {
        if (buffers.size() >= maxBuffers) {
            buffers.poll();                    // evict the oldest before it grows
        }
        buffers.offer(new byte[1024 * 1024]);
    }
}
```

## Why It Happens

The JVM's garbage collector reclaims unreachable objects to free heap. When an
allocation cannot be satisfied after a full GC pass, the JVM has nowhere to get
memory from and aborts with `OutOfMemoryError`. This is a *symptom*: the real bug
is that reachable objects keep accumulating or a single allocation is far too big
for the heap size you configured.

## Solutions

1. Read the suffix: `Java heap space` points at heap consumption, `Metaspace` at generated classes, `unable to create new native thread` at thread/resource limits.
2. Heap-dump the process (`jmap -dump:format=b,file=heap.hprof <pid>` or add `-XX:+HeapDumpOnOutOfMemoryError`) and inspect dominators in a profiler (Eclipse MAT, JFR).
3. Look for `static` collections, caches without eviction, and listener registrations never removed.
4. Stream large inputs (line-by-line, cursor-based iteration) instead of `readAllBytes`/`SELECT *`.
5. Bound in-memory caches with entries that respect memory (Guava/Caffeine with maximum weight).
6. If the workload legitimately needs more memory, raise `-Xmx` — but only after eliminating the leak/boundary bug.

## Prevention

- Set `-XX:+ExitOnOutOfMemoryError` or health probes so the process restarts instead of limping.
- Add load tests that mirror production cardinality (a test passing with 100 rows but failing with 1M rows is a red flag).
- Watch heap metrics in CI/before release and set alerts.
- Prefer bounded collections and explicit eviction policies everywhere state lives long.

## Related Errors

- `StackOverflowError`
- `NoClassDefFoundError`
- `GC overhead limit exceeded` (subcase)
- Python `MemoryError`