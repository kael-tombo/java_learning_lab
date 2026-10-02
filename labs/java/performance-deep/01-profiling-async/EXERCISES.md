# EXERCISES — Async Profiling

## 1. Virtual Thread Profiling (Beginner)

**Goal**: Compare virtual vs platform thread profiling.

```bash
# Run with virtual threads
java -Djdk.virtualThreadScheduler.parallelism=4 -jar app.jar

# Profile
./profiler.sh -d 30 -e cpu -f vt.html <pid>
```

**Tasks**:
1. Identify carrier thread vs virtual thread frames
2. Find pinned virtual threads (`synchronized`, native calls)
3. Compare throughput vs platform threads

---

## 2. StructuredTaskScope Profiling (Beginner)

**Goal**: Profile structured concurrency.

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var f1 = scope.fork(() -> serviceA());
    var f2 = scope.fork(() -> serviceB());
    scope.join();
    scope.throwIfFailed();
}
```

**Tasks**:
1. Profile with async-profiler, observe stack traces
2. Verify parent-child relationship in flame graph
3. Inject failure in one fork, observe cancellation propagation

---

## 3. CompletableFuture Chain Profiling (Intermediate)

**Goal**: Trace async chain with context propagation.

```java
CompletableFuture.supplyAsync(() -> fetchA())
    .thenComposeAsync(a -> fetchB(a))
    .thenComposeAsync(b -> fetchC(b))
    .thenAccept(c -> process(c));
```

**Tasks**:
1. Instrument with OpenTelemetry context propagation
2. Profile with async-profiler, correlate spans
3. Identify context loss points

---

## 4. Reactive Streams Profiling (Advanced)

**Goal**: Profile Reactor pipeline.

```java
Flux.range(1, 1000)
    .flatMap(i -> service.call(i))
    .buffer(100)
    .flatMap(batch -> batchService.process(batch))
    .subscribe();
```

**Tasks**:
1. Add `Hooks.onOperatorDebug()` for operator tracing
2. Profile with async-profiler, identify operator bottlenecks
3. Add Micrometer `Timer` on key operators
4. Profile backpressure behavior under load

---

## 5. Virtual Thread Pinning Detection (Advanced)

**Goal**: Detect and fix pinning.

```bash
# Enable virtual thread events
java -XX:+UnlockDiagnosticVMOptions -XX:+LogVirtualThreadEvents -jar app.jar

# Profile
./profiler.sh -d 30 -e cpu -f vt.html <pid>
```

**Tasks**:
1. Search flame graph for `Thread.isVirtualThreadPinned()`
2. Identify `synchronized` blocks in virtual thread code
3. Replace with `ReentrantLock` or `StampedLock`
4. Re-profile, verify pinning eliminated