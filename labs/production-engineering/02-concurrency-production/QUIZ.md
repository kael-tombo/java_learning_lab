# Lab 02: Concurrency in Production — QUIZ

15 questions. Answer first, then read. Target: 13/15.

---

**Q1. Why is `synchronized` on a `String` a production bug?**
- A) It is slower than `ReentrantLock`
- B) String interning means the lock is global and shared with unrelated code (and with the class loader)
- C) It throws `IllegalMonitorStateException`
- D) It prevents JIT inlining of string methods

**Answer: B** — Locking a shared interned literal can block the entire JVM on a hotspot. Never synchronize on a boxed type, `String`, or `Class`.

---

**Q2. `volatile` guarantees what, precisely?**
- A) Mutual exclusion plus atomicity of compound operations
- B) Visibility of writes and ordering of happens-before; NOT atomicity of `count++`
- C) That the field is never cached in a register
- D) Final-field semantics

**Answer: B** — `i++` is read-modify-write: three operations. `volatile` prevents the JIT from hoisting the read but does not make the sequence atomic. Use `AtomicInteger` or `LongAdder`.

---

**Q3. Which is the correct failure mode diagnosis for a CPU-bound service whose throughput drops 60% at 16 cores?**
- A) Lock contention — add `synchronized`
- B) Coalesced contention / cache-line ping-pong plus false sharing on a shared counter
- C) Insufficient heap
- D) Classloader contention

**Answer: B** — Scale-out that stops helping is a false-sharing or memory-bandwidth signal. Verify with `perf c2c` and try `LongAdder` / striped counters.

---

**Q4. `ThreadLocal` in a servlet container: the standard production mistake is?**
- A) It throws if the value is null
- B) Setting it without `remove()` in a `finally`, leaking per-request state into the pooled thread
- C) It cannot hold large objects
- D) It is not thread-safe

**Answer: B** — Container threads are pooled and long-lived. Un-`remove()`d values leak across requests and retain request-scoped objects (a classic memory-leak source).

---

**Q5. What does `java.util.concurrent` `CompletableFuture.allOf(...).join()` do on a rejected task?**
- A) Waits forever
- B) Throws `CompletionException` wrapping the failure; the *other* futures still run
- C) Cancels all futures
- D) Returns an empty list silently

**Answer: B** — `allOf` fails fast on first exception but does not cancel siblings. This is a classic "we leaked 400 threads on one bad request" pattern.

---

**Q6. A fixed thread pool of size `2N` (`N` = cores) for I/O-bound work is usually wrong because?**
- A) Pools must be power-of-two sized
- B) I/O-bound tasks spend time blocked, so the pool should be sized by concurrency targets, not CPU count
- C) `ThreadPoolExecutor` caps at `Integer.MAX_VALUE`
- D) Virtual threads make any pool size invalid

**Answer: B** — Pool sizing formula differs by task type: `threads = cores * CPUUtilization * (1 + wait/service)`. For DB calls with 100 ms latency, `cores * 1` starves you.

---

**Q7. A `BlockingQueue` with a bounded capacity is used in a producer/consumer service. If the consumer is slower than the producer, what happens when the queue fills?**
- A) Producers block indefinitely and the whole system stalls — you need a rejection policy (fail fast / caller-runs / discard) sized to absorb bursts
- B) The queue grows without bound
- C) Producers get `OutOfMemoryError` immediately
- D) The JVM resizes the queue

**Answer: A** — Back-pressure by design is correct; unbounded blocking *plus* silent stalls is the failure. Always pick and document the `RejectedExecutionHandler`.

---

**Q8. What problem does `ThreadLocalRandom` solve over `Random`?**
- A) Cryptographic randomness
- B) Removing contention on a shared `Random`/`SplittableRandom` instance and avoiding per-thread allocation of `ThreadLocalRandom`
- C) Reproducibility across JVMs
- D) Long-period guarantees

**Answer: B** — `Random`'s CAS loop on a shared `AtomicLong` becomes a scalability cliff. `ThreadLocalRandom.current()` is per-thread and allocation-free.

---

**Q9. Java's `synchronized` is now biased-locking-free and uses which mechanism?**
- A) Dekker/Peterson algorithm
- B) Adaptive spinning, then monitor inflation to a heavyweight `ObjectMonitor`
- C) `ReentrantLock` internally
- D) `VarHandle` compare-and-set

**Answer: B** — Since JDK 15 biased locking was disabled by default; monitors spin briefly then inflate, using a fat lock with a wait set and OS-level parking.

---

**Q10. Double-checked locking without `volatile` is broken because?**
- A) The JIT always locks
- B) Without a happens-before edge, a thread may observe a non-null reference to a partially constructed object
- C) `volatile` is required for `final` fields
- D) The object cannot be `static`

**Answer: B** — This is the Java Memory Model's classic publication bug. Either use `volatile` or an immutable holder class (initialization-on-demand holder idiom).

---

**Q11. Structured concurrency (preview in JDK 21+) improves what?**
- A) Raw throughput
- B) Scoping subtask lifetimes to a lexical block, automatic cancellation, and guaranteed shutdown — removing the "who cancels the executor" class of bugs
- C) Reducing memory footprint
- D) Eliminating locks

**Answer: B** — `StructuredTaskScope` makes cancellation and cleanup provable rather than manual. Still a preview API — pin your JDK and check status.

---

**Q12. Virtual threads (JDK 21) do NOT fix which problem?**
- A) Thread-per-request scalability
- B) Platform thread count limits for blocking I/O
- C) CPU-bound throughput — carrier pool is still `cores` wide
- D) Thread-local-heavy blocking code needing thread-pool redesign

**Answer: C** — Virtual threads are for blocking I/O. CPU-bound work must still be offloaded to a bounded platform-thread pool (`Executors.newVirtualThreadPerTaskExecutor` for I/O, a fixed pool for CPU work).

---

**Q13. A `ReentrantLock` is in use and a thread dies while holding it (uncaught exception). What happens?**
- A) The JVM releases it automatically because `unlock` is in a `finally`
- C) The lock stays held forever if `unlock()` is never called — other threads park permanently
- B) The lock converts to a `synchronized` monitor

**Answer: C** — There is no automatic release; the lock is only released by `unlock()`. (Answer key: **C**.)

---

**Q14. `AtomicIntegerFieldUpdater` / `VarHandle` over `AtomicInteger`: when does it matter?**
- A) Always — atomics are always slow
- B) When you need atomicity over a field in an existing object without adding a wrapper, or hot counters where CAS retry rates are high
- C) Only for `long` fields
- D) Never in user code

**Answer: B** — Both are useful; the real rule is: measure contention first, prefer `LongAdder` for high-contention counters.

---

**Q15. `ForkJoinPool.commonPool()`-based `parallelStream()` in a request handler is dangerous mainly because?**
- A) It deadlocks the HTTP server
- B) It shares a global pool across the whole JVM, so one slow downstream call can starve unrelated requests and block on `ForkJoinPool` managed-blocker escapes
- C) It is not thread-safe
- D) It requires `synchronized` context

**Answer: B** — Global-pool coupling plus `ForkJoinPool.commonPool().parallelism == 1` on single-CPU containers (common in K8s without proper limits) makes it silently serial.

---

## Scorecard
- 15–13: excellent — move to MINI_PROJECT.
- 12–10: re-run EXERCISES focused on JMM and `ThreadLocal` hygiene.
- <10: read THEORY's memory-visibility section cold, then retake in 48h.
