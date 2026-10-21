# Performance Analysis of Java 21 Features

## Virtual Threads Performance

### Throughput Comparison
Virtual threads dramatically improve throughput for I/O-bound workloads:

| Workload | Platform Threads (fixed pool-200) | Virtual Threads | Improvement |
|----------|----------------------------------|-----------------|-------------|
| 10k concurrent sleeps (100ms) | ~5,000 req/s | ~50,000 req/s | 10x |
| Mixed I/O (DB + API calls) | ~2,500 req/s | ~40,000 req/s | 16x |
| CPU-bound (no blocking) | ~8,000 req/s | ~8,000 req/s | ~1x |

The key insight: virtual threads excel when tasks spend time blocked on I/O, because the carrier threads are reused during blocking periods.

### Memory Footprint
- **Platform thread**: ~1 MB stack (default), plus thread metadata (~2 KB)
- **Virtual thread**: ~200 bytes when parked, grows with stack usage but rarely exceeds 10 KB

For 100,000 concurrent requests:
- Platform threads: ~100 GB (impossible for most systems)
- Virtual threads: ~200 MB (easily manageable)

### Pinning Overhead
When virtual threads get pinned (via `synchronized`), performance degrades:

```java
// Bad: Pinning prevents unmounting
synchronized (lock) {
    Thread.sleep(1000);  // Carrier thread blocked for 1 second!
}

// Good: No pinning
lock.lock();
try {
    Thread.sleep(1000);  // Virtual thread unmounts, carrier reused
} finally {
    lock.unlock();
}
```

### Benchmark: Virtual Thread Creation
Creating 1 million virtual threads with a simple task:
```java
long start = System.nanoTime();
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1_000_000; i++) {
        executor.submit(() -> { /* trivial task */ });
    }
}
long elapsed = System.nanoTime() - start;
// ~500ms to create 1M virtual threads (2μs per thread)
```

## Pattern Matching Performance

### instanceof+cast vs Pattern Matching
The compiler generates equivalent bytecode for pattern matching and traditional instanceof casts. There is **zero runtime overhead** for pattern matching. However, record patterns do incur accessor method calls.

### Switch on Type vs if-else Chain
Type patterns in switch are compiled to a `tableswitch` or `lookupswitch` bytecode when the types are sealed with known subclasses, making them O(1) rather than O(n) for if-else chains.

## Record Pattern Performance

Record patterns involve accessor method calls nested. For deep deconstruction:

```java
// This creates multiple accessor calls, but JIT inlines them
if (obj instanceof Line(Point(int x1, int y1), Point(int x2, int y2))) {
    // x1, y1, x2, y2 available directly
}
```

The JIT compiler typically inlines these accessors, making them as fast as direct field access after warmup.

## Sequenced Collections Performance

The `reversed()` view returns a view (not a copy) in `LinkedHashSet` and `TreeSet`, so it is O(1) in memory. For `ArrayList`, `reversed()` returns a `ReverseOrderList$RandomAccess` view that accesses elements via `get(size - 1 - index)`.

## String Template Performance

String Templates were previewed in JDK 21/22 and withdrawn before JDK 23, so there is nothing to benchmark today. The preview's documented design goal was runtime performance comparable to `StringBuilder` concatenation:

```java
// Today's equivalent:
String msg = "Hello %s".formatted(name);
// conceptually builds the same output as:
// new StringBuilder().append("Hello ").append(name).toString();
```

## Structured Concurrency Performance

Structured concurrency adds minimal overhead over raw `ExecutorService`. The `CopyOnWriteArrayList` for tracking subtasks adds linear cost for task management but is negligible for typical fan-out counts (< 100).

### Overhead Breakdown
- Task creation: ~0.5 μs (similar to `CompletableFuture.supplyAsync`)
- Scope join: ~0.1 μs overhead (latch await)
- Cancellation: O(n) where n = number of remaining tasks

## Profiling Recommendations

1. **Use JFR (Java Flight Recorder)**: Record virtual thread events with `jdk.VirtualThreadStart`, `jdk.VirtualThreadEnd`, `jdk.VirtualThreadPinned`
2. **Monitor pinning**: Use `-Djdk.tracePinnedThreads=short` in production to identify scaling bottlenecks
3. **Check carrier thread utilization**: If carrier threads are saturated (100% CPU), virtual threads may be getting pinned excessively
4. **Set parallelism**: Adjust `jdk.virtualThreadScheduler.parallelism` if needed
