# Lab 01: JVM Memory & GC — QUIZ

15 questions. Answer before opening the solution line. Target: 13/15.

---

**Q1. Which heap region is multithreaded by default in HotSpot?**
- A) Eden / Survivor
- B) Old Gen
- C) Metaspace
- D) Code Cache

**Answer: A** — Eden and Survivor are shared by all mutator threads (with per-thread TLAB carving to avoid lock contention). Old Gen is also shared, but the classic answer to "where do most allocations land" is Eden.

---

**Q2. What is the primary difference between G1 and ZGC in production terms?**
- A) G1 is generational, ZGC is not
- B) G1 targets pause times of ~100–200ms, ZGC targets sub-millisecond pauses at terabyte heaps
- C) ZGC requires a Serial collector baseline
- D) G1 cannot do concurrent marking

**Answer: B** — Both are concurrent, but ZGC (colored pointers + load barriers) keeps pauses independent of heap size, at higher CPU and memory overhead.

---

**Q3. `-XX:MaxRAMPercentage=75` sets what exactly?**
- A) Max heap size = 75% of 24GB
- B) Max heap = 75% of detected container memory limit
- C) Max off-heap memory
- D) GC thread count

**Answer: B** — Since JDK 10 the JVM is container-aware and sizes the heap from the cgroup limit, so percentage flags are relative to the container, not the host.

---

**Q4. A `java.lang.OutOfMemoryError: Metaspace` means:**
- A) Heap is too small
- B) Classloader count is unbounded / class metadata leaked
- C) Thread stack too large
- D) Direct buffer exhaustion

**Answer: B** — Metaspace holds class metadata and lives in native memory. Leaks happen when classloaders are never collected (redeployment, dynamic proxies, repeated app-context refresh).

---

**Q5. Why does `-XX:+UseG1GC` still pause longer on a 32GB heap than on a 4GB heap with the same live set?**
- A) Bigger heaps always mean slower GC
- B) Humongous objects and remembered-set maintenance scale with heap size
- C) G1 disables concurrency above 16GB
- D) The JVM picks Serial above 16GB

**Answer: B** — G1 pause time is roughly a function of young-gen size, humongous-region copy work, and RS update overhead, all of which grow with heap size.

---

**Q6. What is the correct fix for `OutOfMemoryError: unable to create new native thread`?**
- A) Increase `-Xmx`
- B) Raise container pids limit and check for thread/connection leaks
- C) Switch to ZGC
- D) Remove `-Xss`

**Answer: B** — Thread stacks are native memory and bounded by the container `pids` cgroup. `-Xmx` is irrelevant here; leaking executors/HikariCP connections is the usual root cause.

---

**Q7. What does `MaxGCPauseMillis` actually control in G1?**
- A) A hard upper bound on every pause
- B) A soft target that guides young-gen sizing heuristics
- C) Full-GC only pauses
- D) Nothing without `-XX:+UseG1GC`

**Answer: B** — It is advisory. G1 will exceed it under pressure; it shapes adaptive sizing so *typical* pauses approach the target.

---

**Q8. Which statement about Metaspace and `-XX:MaxMetaspaceSize` is true?**
- A) Unbounded by default and only reclaimed on Full GC
- B) Bounded by default and reclaimed only on class unload
- C) Identical to CodeCache sizing
- D) Shared with the young generation

**Answer: A** — Metaspace is unbounded by default (since JDK 8) and reclaimed during class unloading, which historically required Full GC; class-unload tuning mitigates this.

---

**Q9. Reading a GC log, `Pause Young (Normal) (G1 Evacuation Pause) 512M->128M(1024M) 24ms` means:**
- A) Heap shrank from 512M to 128M
- B) Live set is 128M; allocation rate made 512M since last GC; 24ms stop-the-world
- C) 512 threads were parked
- D) The heap was resized to 1024M

**Answer: B** — The `before->after(heap)` triple is the canonical way to read G1/serial logs; the live-set-after number is what sizes your heap.

---

**Q10. Why is `-XX:+UseEpsilonGC` (JDK 9+) valuable in production engineering, even though it cannot collect?**
- A) It is the fastest collector for batch jobs
- B) It validates that an application allocates almost nothing, exposing hidden allocation hot spots
- C) It compresses the heap on the fly
- D) It replaces the need for `-Xmx`

**Answer: B** — Epsilon turns any allocation regression into an immediate, deterministic crash at test time — a budget enforcement tool, not a runtime GC.

---

**Q11. Direct (`ByteBuffer.allocateDirect`) memory lives where, and why does it leak silently?**
- A) In the Java heap; it leaks via circular references
- B) In native memory, outside `-Xmx`, so it bypasses heap-based OOM detection
- C) In metaspace
- D) In the CodeCache

**Answer: B** — `sun.misc.Unsafe`/`Bits.reserveMemory` accounting is separate; the classic fix is `MaxDirectMemorySize` plus explicit cleanup.

---

**Q12. TLAB (thread-local allocation buffer) exists primarily to:**
- A) Cache the class metadata of a thread
- B) Let each thread bump-allocate pointers without synchronizing on Eden
- C) Reserve stack space for deep recursion
- D) Pin objects to a CPU

**Answer: B** — Each thread gets a private chunk of Eden and bump-allocates a pointer; refills are the only points that need synchronization.

---

**Q13. A full GC every ~4 hours with a stable 12GB live set and 32GB max heap means:**
- A) The heap is undersized; raise `-Xmx` and stop the full GCs
- B) It is likely `System.gc()` from a library, or promotion failure from humongous allocations — inspect the GC cause first
- C) Add `-XX:+UseSerialGC` to eliminate pauses
- D) Turn on Epsilon to prove allocation is low

**Answer: B** — If live set (12GB) < max heap (32GB), full GCs are not from insufficiency; check `Metadata GC Threshold`, `Humongous Allocation`, or explicit `System.gc()`.

---

**Q14. Which flag combination most reliably lowers GC pause time for a 64GB heap on JDK 21?**
- A) `-XX:+UseParallelGC -Xmx64g`
- B) `-XX:+UseZGC -Xmx64g`
- C) `-XX:+UseG1GC -XX:-UseGCOverheadLimit`
- D) `-XX:MaxGCPauseMillis=1 -XX:+UseG1GC`

**Answer: B** — Generational ZGC (JDK 21) keeps pauses in the sub-millisecond range at 64GB; (D) is a lie the collector will not honor.

---

**Q15. Safepoints and biased locking aside — what does `jcmd GC.heap_info` vs `jmap -histo:live` tell you?**
- A) Both give identical heap snapshots
- B) `heap_info` gives generation sizes/capacity; `histo:live` gives class-level live-object counts (a full GC by default)
- C) `heap_info` lists all live objects; `histo:live` lists JVM flags
- D) Neither forces a GC

**Answer: B** — Histo is the fastest way to find a class whose instance count explains your live set (caches, classloaders, interned strings).

---

## Scorecard
- 15–13: ready for `CODE_DEEP_DIVE` and the mini project.
- 12–10: re-read THEORY sections on generations, TLAB, and collector selection.
- <10: redo `EXERCISES`, then return to this quiz cold after 48 hours.
