# Lab 02: Concurrency in Production — Flashcards

~60 cards. Say the answer before you check it.

---

## Memory & Visibility

Q: What are the three JMM "data race" ingredients?
A: Unsynchronized read/write of shared mutable state + at least one write + no happens-before ordering.

Q: What does `volatile` create?
A: A happens-before edge: writes before the volatile write are visible to reads after the volatile read.

Q: Is `count++` atomic on a `volatile int`?
A: No — read, add, write is three steps; the read-modify-write is not atomic.

Q: What is safe publication?
A: Ensuring a fully-constructed object's reference is not visible before its constructor completes (final fields, volatile, or proper locking).

Q: Why is the initialization-on-demand holder idiom safe?
A: Class initialization is guarded by the JVM's class-init lock, which creates the happens-before edge.

Q: What is a data race's typical symptom?
A: Non-reproducible stale reads, lost updates, `ArrayIndexOutOfBoundsException` on unsafely-published arrays.

Q: Can `final` fields be safely published without volatile?
A: Yes — JMM guarantees correctly constructed final field values are visible after construction completes (with limited caveats for `this` escape).

Q: What is the "this escape" problem?
A: Publishing `this` from a constructor lets other threads see a partially built object; always avoid leaking `this` in constructors.

---

## Locks & Monitors

Q: Why never synchronize on `String`?
A: Interned literals are shared JVM-wide; you would lock against unrelated code and the class loader.

Q: What does biased locking do, and is it on by default in JDK 21?
A: It let a thread acquire a lock without CAS by biasing the object header to that thread. Disabled by default since JDK 15.

Q: When does a monitor inflate?
A: After adaptive spinning fails — from a thin lock to a fat `ObjectMonitor` with a wait set.

Q: `synchronized` vs `ReentrantLock`: three real differences?
A: Lock (fair/reentrant) vs no extra lock object, interruptible acquisition, and `tryLock` timeout.

Q: When is a fair `ReentrantLock` the right choice?
A: When starvation is unacceptable and throughput cost is acceptable; otherwise non-fair is 10x+ faster.

Q: What happens if a thread dies holding a `ReentrantLock` without unlocking?
A: The lock stays held forever; other threads block permanently. There is no automatic release.

Q: `synchronized` is reentrant — does that help with re-locking across the same thread?
A: Yes — same thread re-acquires and increments the hold count; must release equally many times.

Q: What is the `AbstractQueuedSynchronizer` (AQS) idea?
A: A framework for building locks, semaphores, latches, and queues on a single `CLH`-style wait queue.

Q: `CountDownLatch` vs `CyclicBarrier`?
A: Latch = one-shot countdown, one/many threads await zero. Barrier = reusable, all parties must arrive.

Q: `Semaphore` with permits = 10: what does `acquire()` twice from the same thread do?
A: Takes 2 permits; a third acquire blocks until released by any thread.

---

## Atomics & Counters

Q: `AtomicInteger` vs `LongAdder` — when each?
A: `AtomicInteger` when you need the current exact value; `LongAdder` for high-contention counters (sum only).

Q: What is false sharing?
A: Two threads writing different fields that share a cache line, causing coherence traffic that defeats parallelism.

Q: What padding fixes false sharing?
A: `@Contended` (with `-XX:-RestrictContended`), manual padding fields, or striped/`LongAdder` structures.

Q: What is CAS?
A: Compare-and-swap: atomically update only if the current value equals the expected value; returns success.

Q: What is the ABA problem?
A: Value returns to its original between read and CAS, so the CAS succeeds on a stale identity. Fixed by `AtomicStampedReference`.

Q: When does CAS-based counter become a bottleneck?
A: Under contention — failed CAS retries spin and thrash the cache line. That's why `LongAdder` exists.

Q: What does `VarHandle` give over `AtomicIntegerFieldUpdater`?
A: VarHandles support plain, volatile, and opaque/acquire-release access modes and work on any field type.

Q: What is an acquire-release pair?
A: `setRelease`/`getAcquire` — cheaper than full volatile on x86/ARM but still establishes happens-before.

Q: `VarHandle.compareAndSet` vs `weakCompareAndSet`?
A: `CAS` may fail spuriously; `weakCAS` is only guaranteed to succeed if the current value equals expected.

---

## Pools & Executors

Q: Sizing formula for CPU-bound work?
A: `threads ≈ cores + 1`.

Q: Sizing formula for I/O-bound work?
A: `threads ≈ cores × (1 + waitTime/serviceTime)` — or drive it from a concurrency target.

Q: Default `ThreadPoolExecutor` values?
A: core=max=Integer.MAX_VALUE, queue=LinkedBlockingQueue (unbounded), so the pool grows until OOM. Always pass explicit args.

Q: Why is an unbounded queue dangerous in a thread pool?
A: Tasks queue forever, latency grows without limit, and memory grows until OOM — you lose all back-pressure.

Q: `CallerRunsPolicy` — effect?
A: The submitting thread runs the task, providing back-pressure but shifting latency to the caller (may deadlock in nested submits).

Q: `AbortPolicy` vs `DiscardPolicy` — which is safer for payments?
A: `AbortPolicy` — discarding work silently is a data-loss bug.

Q: When does `ForkJoinPool.commonPool().parallelism == 1`?
A: When available processors is 1 — common in misconfigured containers with `cpus: 1` — making `parallelStream()` silently sequential.

Q: What is `CompletableFuture.supplyAsync` default executor?
A: `ForkJoinPool.commonPool()` — a global pool shared JVM-wide. Pass an explicit executor for isolation.

Q: What happens to sibling futures when one stage of `allOf` fails?
A: They keep running; `allOf` fails fast but does not cancel. This is a thread-leak source.

Q: Why is `ThreadPoolExecutor` + `try/finally` shutdown order important?
A: `shutdown()` (graceful) then `awaitTermination(timeout)` then `shutdownNow()` — never skip the await.

---

## Virtual Threads & Modern Concurrency

Q: Virtual threads' core benefit?
A: Cheap, JVM-managed threads for blocking I/O — millions of threads, low memory per thread.

Q: Virtual threads and `synchronized`?
A: They can pin the carrier thread when blocking inside `synchronized`; JDK 24+ reduces this via JEP 491 (reimplemented synchronized). Check JDK status.

Q: When are virtual threads the wrong tool?
A: CPU-bound work, need for thread-local-heavy isolation, or code that assumes bounded thread count (e.g. per-thread native handles).

Q: Correct hybrid pattern?
A: Virtual threads for blocking I/O fan-out; a small fixed platform-thread pool for CPU work via `Executors.newThreadPerTaskExecutor` + explicit executor.

Q: What is a `Semaphore` with virtual threads used for?
A: Limiting actual concurrency (e.g. max 50 in-flight DB calls), not limiting thread count.

Q: What does structured concurrency buy you?
A: Lexically scoped subtasks with automatic cancellation and guaranteed shutdown — no orphaned futures.

Q: What is `Loom`'s carrier-thread pool size?
A: `availableProcessors()` platform threads by default; tune with `-Djdk.virtualThreadScheduler.maxPoolSize`.

Q: Do virtual threads make thread pools obsolete?
A: For I/O fan-out yes; for CPU work no — you still need bounded platform threads.

---

## ThreadLocal & Lifecycle

Q: The canonical `ThreadLocal` bug?
A: Setting without `remove()` in a `finally` inside a pooled-thread servlet — leaking request state and retaining objects.

Q: Why do virtual threads make `ThreadLocal` less dangerous but still present?
A: Each virtual task gets its own thread, so leakage is bounded to the task; but a long-lived task still retains its locals. Use scoped values where available.

Q: `InheritableThreadLocal` hazard?
A: Values copied at thread creation — a pooled child thread inherits a stale value from creation-time context.

Q: What is a thread leak?
A: Threads created but never terminated, holding stack memory and blocking resources; symptom is rising thread count until `OutOfMemoryError: unable to create new native thread`.

Q: What is the `ThreadLocalRandom` advantage?
A: No shared state — removes the CAS contention cliff of `Random` under high thread counts.

---

## Concurrency Diagnostics

Q: First tool for a suspected deadlock?
A: `jcmd <pid> Thread.print` — look for `BLOCKED (on object monitor)` with matching lock owners.

Q: Thread states you actually care about?
A: `RUNNABLE` (including blocked in I/O), `WAITING`/`TIMED_WAITING` (queues/pools), `BLOCKED` (contention — the alarm).

Q: What is `BLOCKED` vs `WAITING`?
A: `BLOCKED` = contending for a monitor; `WAITING` = voluntarily parked on a lock/queue/park.

Q: Where to see lock contention?
A: JFR `jdk.JavaMonitorEnter` events, `perf lock_profile`, or async-profiler.

Q: What does high `RUNNABLE` count with low CPU mean?
A: Threads blocked in native I/O — DB, HTTP, disk. Look at pool saturation and downstream latency.

Q: `jcmd Thread.print` showing thousands of identical `pool-N-thread-M` names?
A: Executor leak — something creates pools per request/task and never shuts them down.

Q: What is `ThreadMXBean.getThreadInfo` useful for?
A: Programmatic thread counts, states, and lock-owner detection for a `/health/diagnostics` endpoint.

Q: Safepoint-related stalls in a concurrent system?
A: Threads must reach safepoints to be paused; long-running loops or JIT deopt can add unmeasured latency.

---

## Patterns

Q: What is the "bulkhead" pattern?
A: Isolated thread pools / semaphores per dependency so one slow downstream cannot exhaust the whole app.

Q: What is "back-pressure" in a reactive/async pipeline?
A: Propagating a demand signal so producers slow down instead of buffering without bound.

Q: What is a "thundering herd"?
A: Many clients retrying a failed dependency at once; mitigate with jittered exponential backoff and caching.

Q: When is a `synchronized` method better than a `ReentrantLock`?
A: Short critical sections, no timeout needed, simpler code — monitors are cheaper.

Q: What is "combining" / "coalescing"?
A: Multiple threads' updates to the same key are merged into one write, e.g. `ConcurrentHashMap.compute` or per-key `CompletableFuture` caching.

Q: What is "double-checked locking with a per-key future" used for?
A: Deduplicating concurrent computation of the same key — a standard cache-stampede fix.

Q: When does `AtomicReference.compareAndSet` suffice instead of a lock?
A: When you can compute the new value outside the CAS loop and the update is idempotent/stateless.

Q: What is ABA-safe retry in a lock-free stack?
A: Tag the head with a version counter, or use `AtomicStampedReference`; CAS alone can corrupt the stack.

---

## Rules of Thumb

Q: Default `ThreadPoolExecutor` queue that surprises you?
A: Unbounded `LinkedBlockingQueue` — pass a bounded queue plus an explicit rejection handler.

Q: Never block inside a `synchronized` block — why?
A: It can pin a virtual thread carrier, and on platform threads it reduces throughput and increases deadlock risk.

Q: Lock ordering rule for avoiding deadlock?
A: Enforce a global, consistent acquisition order across all code paths; document it.

Q: Signal `InterruptedException` properly how?
A: Restore the flag (`Thread.currentThread().interrupt()`) before propagating, so callers can observe cancellation.

Q: What is the "check-then-act" race in a lazy singleton?
A: Two threads both see `null` and both create instances; fix with `volatile` + DCL or the holder idiom.

Q: When is `ConcurrentHashMap.computeIfAbsent` dangerous?
A: Inside a `ConcurrentHashMap`, the mapping function runs while holding the bin lock — a long or reentrant computation blocks other keys in the same bin and can deadlock.
