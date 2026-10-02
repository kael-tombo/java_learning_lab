# THEORY — Async Profiling

## Overview

Async profiling extends traditional profiling to non-blocking, reactive, and async code paths — where traditional stack sampling misses context due to thread hopping, completion stages, and virtual threads.

---

## 1. The Async Profiling Challenge

Traditional profilers sample stack traces at safepoints. In async code:
- Stack traces are fragmented across thread boundaries
- Completion stages create logical but not physical call stacks
- Virtual threads park/unpark, confusing traditional samplers
- Reactive streams decouple producer/consumer threads

**Result**: Traditional flame graphs show fragmented, misleading pictures.

---

## 2. Async Profiling Strategies

### 1. Context Propagation

Pass correlation IDs through async boundaries:

```java
// Manual context propagation
var ctx = Context.current(); // OpenTelemetry context
CompletableFuture.supplyAsync(() -> doWork(), executor)
    .thenApplyAsync(result -> process(result), executor);
```

### 2. Structured Concurrency (JEP 453)

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var future1 = scope.fork(() -> serviceA.call());
    var future2 = scope.fork(() -> serviceB.call());
    scope.join();           // Wait for both
    scope.throwIfFailed();  // Propagate first exception
}
```

StructuredTaskScope preserves parent-child relationships in stack traces.

---

## 3. Virtual Threads & Profiling

Virtual threads (JEP 444) change profiling dynamics:

| Aspect | Platform Threads | Virtual Threads |
|--------|------------------|-----------------|
| Count | ~1000s | Millions |
| Stack trace | Native frames | Virtual + carrier |
| Sampling | OS thread = carrier | Carrier thread = sampling unit |
| Pinning | N/A | `synchronized`, native calls |

**Profiling tips**:
- Use `-XX:+UnlockDiagnosticVMOptions -XX:+LogVirtualThreadEvents`
- Sample carrier threads, correlate with virtual thread IDs
- Pinning detection: `Thread.isVirtual()` + `Thread.isVirtualThreadPinned()`

---

## 4. Reactive Streams Profiling

Reactor / RxJava / Flow profiling challenges:

| Challenge | Solution |
|-----------|----------|
| Operator chain fragmentation | Tag operators with `.tag("stage")` |
| Backpressure signals | Profile `request(n)` / `onNext` latency |
| Scheduler hops | Tag `subscribeOn` / `publishOn` boundaries |
| Operator fusion | Profile fused vs unfused paths |

**Tools**: Reactor's `Hooks.onOperatorDebug()`, Micrometer `Timer` on operators.

---

## 5. Distributed Tracing Integration

Profile across service boundaries:

```java
// OpenTelemetry + W3C TraceContext
var tracer = GlobalOpenTelemetry.getTracer("my-service");
var span = tracer.spanBuilder("operation").startSpan();
try (var scope = span.makeCurrent()) {
    // async work
} finally {
    span.end();
}
```

**Tools**: OpenTelemetry Java Agent, Jaeger, Zipkin, Tempo.

---

## 6. Profiling Tool Matrix for Async

| Tool | Async Support | Best For |
|------|---------------|----------|
| async-profiler | Virtual threads, CompletableFuture, Reactor | Prod CPU/memory |
| JFR | Virtual threads, CompletableFuture, Reactor | Prod all-around |
| JProfiler | Async stacks, Reactor | Dev deep-dive |
| YourKit | Virtual threads, async stacks | Dev deep-dive |
| OpenTelemetry | Distributed traces | Prod tracing |