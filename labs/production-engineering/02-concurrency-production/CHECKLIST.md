# CHECKLIST: Thread Safety in Production
## Lab 02 | Production Engineering Academy

---

## Pre-Deploy Thread Safety Review

### Shared Mutable State
- [ ] All shared mutable fields use thread-safe types (`ConcurrentHashMap`, `AtomicXxx`, `CopyOnWriteArrayList`, etc.)
- [ ] No raw `HashMap` / `ArrayList` / `HashSet` shared across threads
- [ ] Static mutable fields are thread-safe (most dangerous — shared across all instances)
- [ ] Collections returned from APIs are unmodifiable or defensive copies
- [ ] `volatile` used correctly (visibility only, not atomicity for compounds)

### Locks and Synchronization
- [ ] No `synchronized` blocks containing blocking I/O or long operations
- [ ] Lock ordering is consistent across all code paths (prevents deadlock)
- [ ] Every `lock.lock()` has a matching `lock.unlock()` in `finally`
- [ ] `tryLock()` with timeout used where deadlock risk exists
- [ ] No `Object.wait()` without a `while` loop condition check (spurious wakeups)
- [ ] No lock held during network/DB calls

### Thread Pools
- [ ] All thread pools bounded (no `Executors.newCachedThreadPool()` in production)
- [ ] All `BlockingQueue`s bounded (no `LinkedBlockingQueue()` with no capacity limit)
- [ ] Thread factory sets meaningful thread names for debugging
- [ ] Thread pool has `UncaughtExceptionHandler` registered
- [ ] Thread pools shut down gracefully on `@PreDestroy` / shutdown hook
- [ ] Rejection policy is explicit (`CallerRunsPolicy`, `AbortPolicy`, or custom)

### Virtual Threads (Java 21)
- [ ] No `synchronized` around blocking I/O in VT code (pinning check)
- [ ] `-Djdk.tracePinnedThreads=full` run in pre-prod environment
- [ ] DB connection pool bounded via `Semaphore` (not just pool size)
- [ ] `ThreadLocal` usage reviewed for memory impact at scale
- [ ] `ScopedValue` used instead of `ThreadLocal` for read-only context propagation

### Error Handling
- [ ] `InterruptedException` never swallowed — always restore flag or rethrow
- [ ] Worker loops catch exceptions and continue (don't kill the thread on single error)
- [ ] `CompletableFuture` chains have `.exceptionally()` or `.handle()` for error recovery
- [ ] Failed async tasks don't silently disappear (use error callbacks / logging)

### ThreadLocal Lifecycle
- [ ] Every `ThreadLocal.set()` has corresponding `ThreadLocal.remove()` in `finally`
- [ ] ThreadLocal values don't hold large objects (amplified by thread count)
- [ ] Request-scoped data uses Spring `@RequestScope` beans (cleaned automatically)

### Testing Checklist
- [ ] Concurrency bugs tested with multi-threaded tests (JCStress, concurrent JUnit)
- [ ] Deadlock scenario covered by test (two threads transferring in opposite directions)
- [ ] Race condition scenario tested with concurrent stress test
- [ ] Thread pool exhaustion tested (queue full, rejection handling verified)

---

## On-Call Quick Reference: Concurrency Symptoms

| Symptom | Likely Cause | First Action |
|---------|-------------|--------------|
| CPU 100%, no useful work | Infinite loop / deadlock / GC | Thread dump, check for deadlock |
| All threads BLOCKED | Lock contention or deadlock | Thread dump, find the hot lock |
| Memory growing | ThreadLocal leak | Heap dump, search for accumulated TLs |
| 800 req/s (VT, expected 50k) | Carrier thread pinning | `-Djdk.tracePinnedThreads=full` |
| Race condition on counter | Non-atomic `++` | Switch to AtomicInteger/LongAdder |
| Negative inventory | Non-atomic check-then-act | CAS or DB atomic UPDATE |
