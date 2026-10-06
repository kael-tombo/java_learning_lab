# Lab 01: JVM Memory & GC — Flashcards

~60 cards. Cover the answer, say it out loud, then check.

---

## Memory Regions

Q: What lives outside the Java heap?
A: Metaspace (class metadata), CodeCache (JIT), thread stacks, direct/native buffers, GC structures, and the JVM itself.

Q: Which region grew "unbounded by default" in JDK 8+?
A: Metaspace — that is why `-XX:MaxMetaspaceSize` exists.

Q: Why was PermGen removed?
A: It was a fixed-size native region that caused `OutOfMemoryError: PermGen space`; Metaspace grows dynamically and reuses native memory.

Q: What is a TLAB?
A: Thread-Local Allocation Buffer — a private Eden slice enabling lock-free pointer-bump allocation.

Q: When does a TLAB refill cause a safepoint-adjacent pause?
A: On refill or when the remaining chunk is too small; minor (eden allocation slow-path), not a full STW.

Q: Is the Code Cache part of the heap?
A: No. It is native, holds generated JIT code, and has its own sizing and eviction policy (`-XX:+UseCodeCacheFlushing`).

Q: What is a humongous object?
A: In G1, any array/region object larger than half a region; allocated directly into the old gen, which is why one big buffer can force a Full GC.

Q: How is region size chosen by G1?
A: `-XX:G1HeapRegionSize` in power-of-two MB, constrained to 1–32MB and roughly heap/2048 target.

Q: What is Metaspace fragmentation?
A: Unloading/loading classes leaves unreclaimed committed native memory, so committed != used; `jcmd VM.metaspace` shows both.

---

## Collectors

Q: Default collector on JDK 11–17?
A: G1GC. On JDK 8 it was ParallelGC. On small heaps the JVM may pick SerialGC.

Q: G1's core partitioning idea?
A: Divide heap into equal regions, collect the young generation per-region ("garbage first") to build a contiguous old-gen space for compaction.

Q: What does "Concurrent Mark" mean in G1?
A: Marking the live object graph happens concurrently with mutators using SATB write barriers, so marking pauses are short.

Q: What is SATB?
A: Snapshot-At-The-Beginning — G1 keeps the old value in the write barrier so deletions during concurrent marking are remembered.

Q: ZGC's key trick for short pauses?
A: Colored pointers + load barriers; marking pointers in GC-safe colors so relocation is atomic metadata change, not a copy of object bytes.

Q: Does ZGC compact?
A: Yes — concurrently, using relocation sets, so no humongous penalty like G1.

Q: Shenandoah's differentiator?
A: Concurrent compaction of the whole heap, including generational, aimed at O(pauses independent of heap size) on smaller heaps than ZGC's target.

Q: When is ParallelGC a legitimate choice?
A: Batch/analytics jobs and low-allocation-rate services where throughput beats pause predictability.

Q: What is EpsilonGC's purpose?
A: Validate zero-allocation designs by failing fast; a test-time GC, not a production GC.

Q: What does `-XX:+UseAdaptiveSizePolicy` do (default true)?
A: Lets the collector choose young/old sizes and evacuation budgets each cycle based on pause goals and allocation history.

---

## Sizing & Flags

Q: What does `-XX:MaxRAMPercentage` compute against?
A: The container memory limit (cgroup v1/v2), not host RAM — critical in Kubernetes.

Q: When should you set `-Xms == -Xmx`?
A: Long-running services where heap resizing causes pauses and you have measured the needed live set.

Q: What is a good first heap sizing heuristic?
A: Live set after a full GC at peak × 3, then validate with a load test; never guess from request rate alone.

Q: What does `MaxGCPauseMillis` NOT do?
A: It does not cap pauses; it feeds the adaptive sizing heuristics as a soft target.

Q: What does `InitiatingHeapOccupancyPercent` control?
A: When G1 starts concurrent marking (as a percentage of old-gen occupancy), typically 45; lower it for fast allocation rates.

Q: What does `G1PeriodicGCInterval` do?
A: Optionally forces a periodic GC (e.g. at off-peak hours) to avoid allocation failure after very long uptime.

Q: What is `-XX:+HeapDumpOnOutOfMemoryError` for?
A: Writes a heap dump to `-XX:HeapDumpPath` on OOM — your single most valuable diagnostic artifact.

Q: What does `-XX:+ExitOnOutOfMemoryError` do?
A: Kills the JVM immediately on OOM so the orchestrator restarts a clean process instead of limping on.

Q: How do you bound direct memory?
A: `-XX:MaxDirectMemorySize=` plus a `Cleaner`-based release path; otherwise OOM manifests as `OutOfMemoryError: Direct buffer memory`.

Q: What does `-XX:+AlwaysPreTouch` cost?
A: Touches every page at startup (slower boot, RSS visible to the scheduler) but removes page-fault cost later.

Q: What is `-XX:+UseContainerSupport`?
A: Default-on since JDK 10: JVM reads cgroup limits for heap and CPU ergonomics.

Q: What is a GC ergonomics problem with `-Xmx` unset in a container?
A: The JVM may size heap from host RAM, see far more "free" memory than allowed, and get OOM-killed by the kernel.

---

## Reading Logs

Q: Decode `Pause Young (Normal) (G1 Evacuation Pause) 512M->128M(1024M) 24ms`.
A: 512M before, 128M live after, 1024M total heap capacity, 24ms STW pause.

Q: What is the `Cause` line useful for?
A: `G1 Evacuation Pause` (normal), `G1 Humongous Allocation`, `G1 Preventive Collection`, `Metadata GC Threshold` — each points to a different root cause.

Q: What is `To-space exhausted`?
A: Survivor space cannot hold surviving objects; objects are tenured early or a Full GC is triggered. Fix with more survivor space / bigger young gen.

Q: What is `System.gc()` in a log?
A: A full collection requested by application code (e.g. some caches, JMX, or `Runtime.gc()` in tests) — often the true cause of "random" full GCs.

Q: What does `Concurrent Mark Cycle` vs `Pause Remark` mean?
A: Cycle is the concurrent phase; Remark is a short STW pause to finish marking and re-scan dirty cards.

Q: What does `Evacuation Failure` signal?
A: Old-gen regions couldn't free space fast enough → heap too tight or humongous pressure. Not a GC bug.

Q: Where are JVM exit-time GC warnings?
A: `onError`/`onExit` log dumps: `jcmd $PID GC.heap_dump` triggers a dump for post-mortem analysis.

Q: What does `-Xlog:gc*,safepoint:file=gc.log:time,uptime,level,tags` add?
A: Safepoint logging — shows why the JVM stopped (biased-lock revocation, deoptimization, class loading).

---

## Diagnostics

Q: Best first command for a suspected leak?
A: `jcmd <pid> GC.heap_info` (free, no pause) then `jcmd <pid> GC.class_histogram` (forces Full GC).

Q: How do you capture a heap without restarting?
A: `jcmd <pid> GC.heap_dump /path/heap.hprof` (triggers Full GC unless `-all`).

Q: Which tool shows per-generation committed vs used?
A: `jstat -gcutil <pid> 1000` and `jcmd <pid> GC.heap_info`.

Q: Which flags reveal GC-native memory?
A: `-XX:NativeMemoryTracking=summary` + `jcmd <pid> VM.native_memory summary`.

Q: How do you count threads and spot leaks?
A: `jcmd <pid> Thread.print` — group by name; a growing pool of identical `pool-N-thread-M` is the leak.

Q: How do you find classloader leaks?
A: Dump heap, run a dominator/retained-size analysis; look for `java.lang.Class` retained by a live thread/context.

Q: What does "retained size" mean?
A: Bytes that would be freed if the object were collected — the correct way to attribute memory, unlike shallow size.

Q: What is safepoint bias?
A: The extra time a thread takes to reach a safepoint, causing pauses longer than GC log timings.

Q: How do you detect allocation rate?
A: `before→after` heap deltas over time in GC logs, or `jcmd <pid> GC.class_histogram` churn under load.

Q: Allocation rate heuristic for sizing young gen?
A: Keep pause count low by making young gen ≈ live set ÷ target survival ratio × (1 / pause target seconds).

Q: What's the OOM triage order?
A: Which OOM type → metaspace vs heap vs direct vs native thread → histo/dump → find the dominant class → fix leak or resize.

Q: When is bigger heap the wrong fix?
A: When the live set is small and growth comes from short-lived garbage (reduce allocation) or humongous buffers (chunk them).

Q: JVM-native vs container OOM-kill — how to tell?
A: Kernel OOM-kill means no `java.lang.OutOfMemoryError` in logs and exit code 137; JVM OOME has a stack trace.

Q: Why does `-XX:+ExitOnOutOfMemoryError` help on Kubernetes?
A: A deterministic crash → CrashLoopBackOff → clean restart, instead of a degraded pod holding stale state.

Q: What's the safe way to test GC changes in prod?
A: One variable per canary, compare p99 pause and allocation rate from the same window, and keep `-XX:+ExitOnOutOfMemoryError`.
