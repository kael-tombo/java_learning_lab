# VISION — Lab 02: Concurrency in Production

> From "it's thread-safe" to "I know exactly which line will fail under load, and why."

---

## The Arc

1. **Memory model fluency** — happens-before, safe publication, data races, final-field semantics.
2. **Lock mechanics** — thin/fat monitors, biased locking's retirement, `ReentrantLock`, AQS.
3. **Atomic design** — CAS, ABA, false sharing, `LongAdder` vs `AtomicInteger`, VarHandles.
4. **Pool economics** — sizing formulas, bounded queues, rejection policy, back-pressure.
5. **Lifecycle hygiene** — `ThreadLocal` cleanup, executor shutdown, thread-leak detection.
6. **Modern concurrency** — virtual threads, structured concurrency, semaphores for real limits.
7. **Diagnosis** — deadlock triage, contention analysis, thread-state forensics.

---

## Why this lab exists

Concurrency bugs are the hardest class of production defect: they are non-deterministic, they hide behind load, and "fixed" code that merely reduced probability gets celebrated. Most teams learn concurrency from interview patterns and then ship request-scoped `ThreadLocal`s into pooled containers.

The specific goal here: **you can look at a service's concurrency configuration and predict its failure mode under a traffic spike, dependency slowdown, or partial outage — before it happens in production.**

---

## Milestones (checkable)

- [ ] M1: Explain a data race with a happens-before diagram, and predict the outcome of the double-checked-locking bug without running it.
- [ ] M2: Write a service where `synchronized`, `ReentrantLock`, and atomics are each used for a reason you can defend aloud.
- [ ] M3: Size a thread pool for a stated service profile using Little's Law and Erlang C, showing the arithmetic and the `ρ` you targeted.
- [ ] M4: Produce a thread-leak in a lab harness, detect it with `jcmd Thread.print`, and fix it.
- [ ] M5: Demonstrate the `ThreadLocal` leak in a servlet-style pooled container and prove the fix with a heap histogram.
- [ ] M6: Convert a CPU-bound + I/O-bound service to virtual threads with a semaphore bounding the expensive operation, and show the CPU-bound part is unaffected.
- [ ] M7: Diagnose a planted deadlock and a planted false-sharing bottleneck from thread dumps and `perf c2c` output.

---

## Anti-Goals

- Shipping `synchronized` on a shared object as a "quick fix" without understanding contention.
- Unbounded `LinkedBlockingQueue` in a `ThreadPoolExecutor`, discovered later in prod.
- `ThreadLocal` without `remove()`, framed as a code-style issue rather than a leak source.
- Assuming thread safety of a collection transitively implies safety of the objects inside it (`ConcurrentHashMap<MutableThing>` is not safe).
- Migrating everything to virtual threads and calling concurrency solved.
- Treating a deadlock as an exotic edge case rather than a design defect with a known prevention rule.

---

## Interview Lens

- "Your service uses a pool of 200 threads against a DB with 100 ms p99 latency. What happens at 4000 rps?"
- "How would you detect a thread leak in a running JVM?"
- "Explain false sharing and how you found it in production."
- "When would you *not* use `synchronized`?"
- "What breaks when you move a thread pool to virtual threads?"

---

## 30-Day Plan

- **Week 1** — THEORY on the JMM, happens-before, and monitor inflation; hand-draw the race examples. M1–M2.
- **Week 2** — EXERCISES: sizing drills, deadlock hunts, contention microbenchmarks; QUIZ to 13/15; FLASHCARDS daily. M3.
- **Week 3** — MINI_PROJECT: build the executor + bulkhead + leak-detection harness. M4–M5.
- **Week 4** — REAL_WORLD_PROJECT war story and the concurrency design review; teach-back: "our pool sizing, defended" in 5 minutes. M6–M7.

---

## Artifacts you should be able to show

1. A pool-sizing calculation sheet: `λ`, `W`, `ρ`, resulting `P`, and headroom policy.
2. A thread-leak reproduction plus the `jcmd Thread.print` evidence and fix.
3. A `ThreadLocal` leak demo with before/after class histograms.
4. A deadlock thread dump with the cycle annotated.
5. A bulkhead configuration with per-dependency concurrency limits and rationale.

---

## Done = You Can

- Given a service's traffic profile and dependency latencies, size its pools and justify the numbers.
- Identify a data race, a deadlock, a livelock, and a thread leak from evidence, not vibes.
- Explain what changes and what does not when you adopt virtual threads.
- Design concurrency so that one slow dependency degrades gracefully instead of collapsing the process.
