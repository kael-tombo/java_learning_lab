# Lab 03: Production Debugging — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. Your service's p99 latency doubled but the mean is unchanged. What does that most strongly suggest?**
- A) A uniform slowdown
- B) A tail-only problem: GC, lock contention, or a downstream dependency with a bimodal latency distribution
- C) Increased traffic
- D) CPU throttling

**Answer: B** — Mean-stable/p99-worse is the signature of added variance, not added work. GC pauses and lock waits add variance; a uniform downstream slowdown moves both.

---

**Q2. A `ThreadMXBean`/`jstack` dump shows 60% of threads `RUNNABLE` with low CPU usage. Where are they?**
- A) Spinning in user code
- B) Blocked in native I/O (socket read, disk, `fsync`) — `RUNNABLE` includes native blocking
- C) Deadlocked
- D) In the JIT

**Answer: B** — This is one of the most common misreadings. Native I/O shows as `RUNNABLE`. Correlate with the thread dump's stack top frames and with network/DNS metrics.

---

**Q3. Which flags must you add to diagnose a suspected deadlock properly?**
- A) `-XX:+PrintCompilation`
- B) `jstack` / `jcmd Thread.print` — plus on JDK 21 `jcmd <pid> Thread.print -l` for lock ownership
- C) `-verbose:class`
- D) `-Xss512k`

**Answer: B** — `Thread.print -l` includes the monitor owner, which is what turns a pile of blocked threads into a readable cycle.

---

**Q4. Your heap looks fine but the service dies with `OutOfMemoryError: unable to create new native thread`. Where do you look?**
- A) `-Xmx`
- B) Container `pids` limit, thread count, and per-thread native memory (stacks + JNI + direct buffers) — not the Java heap
- C) Metaspace only
- D) The CodeCache

**Answer: B** — Native thread exhaustion is bounded by the container's `pids` cgroup and total native memory, never by `-Xmx`.

---

**Q5. What is the strongest single clue that a latency spike is GC, not the application?**
- A) High CPU
- B) A correlated dip in `jvm_gc_pause_seconds` / a `Pause Young` line at the same timestamp in GC logs
- C) A spike in 500s
- D) A slow query log entry

**Answer: B** — Correlation on the same timestamp with an actual GC log line is proof; everything else is inference. Require both signals.

---

**Q6. `jcmd <pid> VM.native_memory summary.diff` is valuable because?**
- A) It shows all Java objects
- B) It diffs native memory categories against a prior baseline, isolating thread stacks / code cache / metaspace / GC overhead growth
- C) It triggers a full GC
- D) It profiles CPU

**Answer: B** — Native memory is invisible to heap tools. `baseline` → workload → `summary.diff` is the standard technique.

---

**Q7. A service is CPU-throttled by cgroups. What is the actual symptom signature?**
- A) 100% CPU with no work
- B) Rising latency while observed CPU sits below the limit, with `container_cpu_cfs_throttled_seconds_total` increasing
- C) OOM-kill
- D) GC pauses only

**Answer: B** — CFS throttling means the container's quota was exhausted within a 100 ms period, so CPU *appears* underused in long-window graphs while latency spikes. Check the throttling counter, not the CPU graph.

---

**Q8. Which of these is a valid way to prove a suspected race condition in production?**
- A) Add `synchronized` and see if it goes away
- B) `jcmd Thread.print` in a tight loop hunting for inconsistent state, plus JFR `jdk.JavaMonitorEnter` / lock analysis, plus a targeted stress test in a staging environment
- C) Read the code until convinced
- D) Enable `-Xcheck:jni` in prod

**Answer: B** — A race is by definition nondeterministic; production evidence must be statistical (repeated observations with timestamps) plus a reproducible stress test. "It went away" is not proof.

---

**Q9. What does a `Thread.State.BLOCKED` thread tell you, exactly?**
- A) The thread is doing slow I/O
- B) The thread is blocked acquiring a monitor — real contention — and the dump names the owner
- C) The thread is in the garbage collector
- D) The thread is parked waiting on a lock or queue (that's `WAITING`)

**Answer: B** — `BLOCKED` is *only* monitor contention. `WAITING`/`TIMED_WAITING` are voluntary parks (pools, queues, `sleep`, `Future.get`). Conflating them misleads triage.

---

**Q10. A thread dump taken once is weak evidence because?**
- A) `jstack` is unreliable
- B) It is a single sample of a stochastic system — you need repeated dumps over time to see a consistent pattern
- C) It perturbs the JVM too much
- D) It only shows 10 threads

**Answer: B** — Multiple timed dumps (or a continuous sampler like JFR/`honest-profiler`) turn anecdote into a pattern. One dump rarely shows the bug in action.

---

**Q11. Application-level debugging in production should prefer which tool?**
- A) Attaching a debugger and stepping through code
- B) Remote diagnostics endpoints, log/trace correlation, and continuous profiling (JFR, async-profiler) with minimal overhead
- C) Console logging of every statement
- D) Reproducing locally

**Answer: B** — Production debugging is an observability discipline, not an interactive one. Anything that perturbs the process significantly is reserved for reproductions.

---

**Q12. Which JFR events answer "where is the time actually going"?**
- A) `jdk.GarbageCollection` only
- B) `jdk.ExecutionSample` (CPU) + `jdk.JavaMonitorEnter` (lock wait) + `jdk.ThreadPark` (queue waits) + `jdk.SocketRead` (I/O wait)
- C) `jdk.ClassLoad` only
- D) `jdk.YoungGarbageCollection`

**Answer: B** — Distinguishing CPU / lock / park / I/O wait is *the* essential triage split. Sampling CPU alone under-samples blocked threads and gives a confidently wrong answer.

---

**Q13. `OutOfMemoryError: Metaspace` mid-deploy usually means?**
- A) Heap too small
- B) Classloaders (e.g. per-deploy or per-request) are never collected, so class metadata accumulates
- C) Direct buffer exhaustion
- D) Too many threads

**Answer: B** — Metaspace grows with loaded classes and is reclaimed only on class unloading; unreferenced classloaders pin their classes.

---

**Q14. Your heap dump analysis says a `HashMap` retains 4 GB. Before blaming the map, what must you verify?**
- A) That it is a `HashMap` and not a subclass
- B) Whether it is *retained* legitimately (it is the application's real live set) or leaked — check dominators, the path from GC roots, and whether the key/value objects are still referenced
- C) Its `hashCode` implementation
- D) Its iteration order

**Answer: B** — Retained size tells you what would be freed, not whether freeing it is correct. Always walk the dominator path to the GC root before declaring a leak.

---

**Q15. What makes a "good" production debugging habit, most of all?**
- A) Fast reflexes
- B) Pre-instrumented systems: correlation IDs, dashboards keyed by the symptoms you might see, and rehearsed runbooks — so the first 5 minutes produce evidence rather than guesses
- C) Using `kill -9` liberally
- D) Always reading source code first

**Answer: B** — Debugging speed is a *design* property. Systems instrumented for their known failure modes are debuggable; others are not.

---

## Scorecard
- 15–13: ready for CODE_DEEP_DIVE + MINI_PROJECT.
- 12–10: re-read THEORY on thread states, JFR events, and native memory.
- <10: redo EXERCISES with repeated thread dumps, then retake cold in 48h.
