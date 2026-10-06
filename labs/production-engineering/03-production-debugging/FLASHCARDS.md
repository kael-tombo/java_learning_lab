# Lab 03: Production Debugging — Flashcards

~60 cards. These are the commands and the triage rules you need reflexively.

---

## First 5 Minutes

Q: What are the first three questions in any prod incident?
A: What changed? What is the blast radius? What is the fastest mitigation (rollback, shed, disable)?

Q: What single command tells you if the process is alive and what state it is in?
A: `jcmd <pid> VM.flags` / `GC.heap_info` / `Thread.print` — any `jcmd` call doubles as a liveness probe of the JVM.

Q: `jcmd <pid> help` — why run it early?
A: It confirms attach works and lists every diagnostic available on that JVM version.

Q: What should you capture before restarting anything?
A: Thread dumps (3–5, spaced), heap histogram, GC log tail, NMT baseline/diff, metrics snapshot, and the current command line.

Q: Why capture before restart?
A: The bug is live for about 90 seconds; after restart you have only the aftermath.

---

## Thread Diagnostics

Q: All six Java thread states?
A: `NEW`, `RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`, `TERMINATED`.

Q: What does `BLOCKED` *only* mean?
A: Contended monitor acquisition. Never I/O, never parking.

Q: What do `WAITING` and `TIMED_WAITING` cover?
A: Voluntary parks: `Object.wait`, `LockSupport.park`, pool queues, `Future.get`, `Thread.sleep` (timed).

Q: Why is `RUNNABLE` ambiguous?
A: It includes threads blocked in native `read()`/`recv()`/disk. The stack top frame disambiguates.

Q: Command to dump threads with lock ownership?
A: `jcmd <pid> Thread.print -l` (or `jstack -l <pid>`).

Q: How many dumps for a decent picture?
A: 3–5, spaced 2–10 s apart, or run a 30 s loop. One dump is an anecdote.

Q: Thread state histogram — what are you looking for?
A: A dominant state. `WAITING` majority = pool/queue saturation. `BLOCKED` majority = lock contention. `RUNNABLE` + low CPU = native I/O.

Q: What pattern signals a thread leak?
A: Monotonic growth of identically-named threads across dumps (`pool-N-thread-M`).

Q: Where do you look for the "waiting" thread's target?
A: The `waiting to lock` / `- waiting on` / `parking to wait for` lines, plus `Locked ownable synchronizers`.

Q: What is a livelock vs deadlock?
A: Deadlock = threads blocked forever; livelock = threads spin/retry, consuming CPU, making no progress.

Q: What does `-XX:+HeapDumpOnOutOfMemoryError` do and where does it write?
A: Dumps heap to `-XX:HeapDumpPath` on OOM; large files — ship them off-pod promptly.

Q: Thread dump overhead?
A: A safepoint pause, typically single-digit milliseconds to tens of ms. Safe, but do not spam it at high frequency.

---

## Heap Diagnostics

Q: Cheapest heap command, no GC triggered?
A: `jcmd <pid> GC.heap_info`.

Q: Class histogram and its cost?
A: `jcmd <pid> GC.class_histogram` — full GC by default; add `-all` to skip the GC.

Q: Histogram vs heap dump — when each?
A: Histogram for "which class dominates?" (fast); dump for "why is it retained?" (slow, big).

Q: What is shallow vs retained size?
A: Shallow = object alone. Retained = bytes freed if this object were collected (dominator tree). Only retained size reveals leaks.

Q: Dominator tree answers what question?
A: "What single object, if removed, would free this memory?" — the classic leak-attribution tool.

Q: Reachability roots?
A: Static fields, thread stacks/locals, JNI globals, and interned strings. Leak paths start here.

Q: `GC.class_histogram` diffing over time?
A: The fastest leak detector — run it on a schedule, diff counts per class, alert on growth.

Q: Live-set computation from GC logs?
A: The `after` value of each collection is a live-set estimate; take a max over a window.

Q: When is a heap dump unsafe?
A: When the process is memory-starved (dumping may fail) or the heap is many GB and disk is tight. Prefer histogram first.

Q: What does `-XX:HeapDumpPath` need to be?
A: A writable volume with room for a file the size of the live set — a common prod surprise (filled ephemeral disk).

---

## Native Memory

Q: Which memory is invisible to heap tools?
A: Metaspace, code cache, thread stacks, direct/native buffers, GC data structures, mapped files, JNI.

Q: How do you enable native memory tracking?
A: `-XX:NativeMemoryTracking=summary` (or `detail`); must be on at startup.

Q: The three-step NMT workflow?
A: `jcmd <pid> VM.native_memory baseline` → run workload → `jcmd <pid> VM.native_memory summary.diff`.

Q: How much thread stack memory does 500 threads × 1 MB `-Xss` take?
A: ~500 MB native — easily the largest native consumer in an IO service.

Q: Direct memory accounting?
A: Bounded separately via `-XX:MaxDirectMemorySize`; exceeding it throws `OutOfMemoryError: Direct buffer memory`.

Q: `OutOfMemoryError: unable to create new native thread` implies?
A: Process/thread limits or native memory exhaustion (container `pids`), *not* heap.

Q: Resident Set Size vs heap committed?
A: RSS = heap *touched* + all native + stacks. Committed heap ≠ RSS; `AlwaysPreTouch` makes them match.

---

## CPU & Profiling

Q: Lowest-overhead way to find CPU hot spots in prod?
A: JFR `jdk.ExecutionSample` with `settings=profile` (~1–2% overhead), or async-profiler wall-clock mode.

Q: `jdk.ExecutionSample` vs `jdk.NativeMethodSample`?
A: Java frames vs native frames — you need both or you attribute time to the wrong layer (socket reads, syscalls).

Q: Which JFR events reveal blocking?
A: `jdk.JavaMonitorEnter` (lock), `jdk.ThreadPark` (queue/park), `jdk.SocketRead`/`SocketWrite` (I/O), `jdk.FileRead`.

Q: Why is sampling better than a debugger in prod?
A: No perturbation, runs continuously, works on a live process, statistically representative.

Q: `top` showing 100% CPU — first two checks?
A: (1) Is it the JVM or a native/GPU/agent process? (2) Which threads? Then get a JFR/profile dump of the hot method.

Q: A CPU-bound hotspot at exactly N threads — suspect?
A: Lock contention spinning or a busy-wait retry loop; contention shows up as CPU, not as `BLOCKED`.

Q: `kill -3` vs `jcmd`?
A: `kill -3` prints to stdout of the JVM process (may be swallowed by the container runtime); `jcmd` is explicit and reliable.

---

## Container & Kubernetes Debugging

Q: Exit code 137 means?
A: SIGKILL — usually OOM-kill (cgroup memory) or a liveness-probe kill. No JVM OOME in the log means kernel kill.

Q: Exit code 143?
A: SIGTERM — normal Kubernetes termination.

Q: Where do you see cgroup CPU throttling?
A: `container_cpu_cfs_throttled_seconds_total` (cAdvisor/Prometheus) or `cpu.stat` in the cgroup.

Q: Throttled-but-not-100%-CPU symptom?
A: The container hit its quota within a 100 ms CFS period; long-window CPU averages hide it while latency spikes.

Q: JVM in a container: which memory does it see?
A: The cgroup limit (since JDK 10 with UseContainerSupport). Verify with `jcmd <pid> VM.flags` and `Runtime.maxMemory()`.

Q: Why is `-Xmx` = container limit dangerous?
A: No room for metaspace, code cache, stacks, direct buffers → kernel OOM-kill with no OOME.

Q: Reading logs from a crashed pod?
A: Previous container logs (`kubectl logs --previous`), plus any log shipped to stdout before exit.

Q: Ephemeral-storage `no such file or directory` on a heap dump?
A: Ephemeral volume full or not mounted at that path — a classic prod-only heap-dump failure.

---

## Debugging Discipline

Q: Correlation ID — why is it the highest-leverage debugging tool?
A: It joins client, gateway, service, DB, and log lines into one trace across process boundaries — turns guessing into reading.

Q: What must every log line have?
A: Timestamp (with tz + ms), level, correlation/trace ID, thread name, message, and key attributes. No ID = undebuggable.

Q: Why structured logs beat string logs?
A: Machine-queryable fields; you can filter and aggregate without brittle regex.

Q: Sampling vs full logging at high volume?
A: Full logs are the last line of defense — they cost money and rarely contain what you need; prefer metrics/traces + sampled logs.

Q: Should you ever add a debug log to prod to diagnose?
A: Only as a bounded, sampled, kill-switchable feature flag. Never an un-gated `System.out`.

Q: What is the "five whys" trap in debugging?
A: Stopping at the proximate cause (OOM) instead of the systemic cause (unbounded cache).

Q: Reproduce first, or fix first?
A: Reproduce (or at least characterize precisely) first; unreproduced fixes are guesses that often regress.

Q: When is a staging repro insufficient?
A: When the trigger is a production-only interaction (traffic shape, data skew, config, version mix) — then add production-shaped load or shadow traffic.

Q: What should a postmortem capture about debugging difficulty?
A: "Time-to-diagnose," which quantifies your observability gaps and prioritizes the next instrumentation investments.

---

## Triage Cheat Sheet

Q: Latency up, CPU flat, one dependency slow → check first?
A: That dependency's client-side metrics (timeouts, retries, in-flight), and thread states in `WAITING` on I/O.

Q: Latency up, CPU at limit → check first?
A: Hot method from JFR; then contention; then whether the work is necessary.

Q: Latency up only for some users → check first?
A: Data skew, cache-key variance, or tenant-specific config; a per-tenant metric split is the fastest discriminator.

Q: Errors cluster in one region/zone → check first?
A: That zone's node health, network path, and any leader/primary there.

Q: Everything fine until deploy → check first?
A: Config/flag/env diff between versions, plus anything data-dependent the new version touched.

Q: Intermittent, unreproducible slowness → first tool?
A: Continuous profiling (JFR/async-profiler) with `ThreadPark` + `SocketRead` + `JavaMonitorEnter` enabled.

Q: `OutOfMemoryError: Java heap space` → first three commands?
A: `jcmd <pid> GC.class_histogram` → check heap dump presence → `jcmd <pid> GC.heap_info`.

Q: `OutOfMemoryError: Metaspace` → first check?
A: Classloader count and whether anything creates classloaders per request/deploy (`jcmd <pid> VM.classloader_stats`).

Q: `OutOfMemoryError: Direct buffer memory` → fix pattern?
A: Bound with `-XX:MaxDirectMemorySize`, release explicitly (try-with-resources / `Cleaner`), and check for per-request direct allocation.

Q: GC pauses correlate with deploys → suspect?
A: Class loading + JIT warmup on new pods, or cache warmup; check `jdk.ClassLoad` and first-N-minutes GC logs.
