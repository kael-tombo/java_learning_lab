# INTERVIEW QUESTIONS: Production Debugging & Profiling
## Lab 03 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: An application pod in production is consuming 100% CPU. How do you find the exact line of code causing it within 5 minutes?
**Answer**:
1. Run `top -H -p <PID>` to list all threads in the JVM ordered by CPU consumption. Identify the `TID` of the top thread.
2. Convert that TID to hexadecimal: `printf "0x%x\n" <TID>`.
3. Capture a thread dump via `jcmd <PID> Thread.print` or `kill -3 <PID>`.
4. Search the thread dump for `nid=<hex_tid>`.
5. The stack trace associated with that `nid` reveals the exact class, method, and line number spinning on CPU (e.g. an infinite loop, regex backtracking, or unthrottled spinlock).

### Q2: What is "Safepoint Bias" and why does it render standard sampling profilers inaccurate?
**Answer**:
Standard JVM profilers that use JVM TI `GetAllStackTraces` can only sample threads when all threads are brought to a JVM safepoint. Safepoints are only placed at certain locations (like method returns, loop back-edges, or allocation points). If a thread spends significant time in a tight, uncounted loop compiled by C2 (which omits safepoint polls), it cannot be sampled until it exits the loop. The profiler mistakenly attributes the time to the subsequent method. `async-profiler` overcomes this by using OS `SIGPROF` signals and `AsyncGetCallTrace`, which capture stack traces anywhere without waiting for safepoints.

---

## Staff / Principal Level (8+ Years)

### Q3: A microservice experiences random 3-second p99 latency spikes once every two hours, but GC logs show all pauses are under 15ms. How do you diagnose this?
**Answer**:
1. **JVM Safepoints Unrelated to GC**: Inspect safepoint pause times via `-Xlog:safepoint=debug`. Operations like RevokeBias (legacy), ThreadDump, Deoptimization, or Class Redefinition stop all threads without appearing in GC logs.
2. **Time-To-Safepoint (TTSP)**: A thread may take 2.9 seconds to reach a safepoint because it is in a long loop without safepoint polls. All other threads are halted waiting for it. The flag `-XX:+PrintSafepointStatistics` / `-Xlog:safepoint` highlights TTSP vs safepoint execution time.
3. **OS-level CFS Throttling**: In Kubernetes, if CPU limits are set, the CFS (Completely Fair Scheduler) quota can throttle the container for hundreds of milliseconds if the thread pool bursts past quota within a 100ms quota period. Check `/sys/fs/cgroup/cpu/cpu.stat` for `nr_throttled`.
4. **Kernel I/O Stall**: Swapping, page cache flushes, or synchronous file logging stalling an event loop thread. Check using `vmstat 1`, `iostat -xz 1`, or eBPF `biolatency`.

### Q4: Design a production continuous profiling system for a 1,000-node Kubernetes fleet.
**Answer**:
- **Agent**: Lightweight eBPF or JFR/async-profiler agent embedded in application runtime or daemonset.
- **Overhead Budget**: Hard ceiling at 1% CPU, 30MB RAM.
- **Sampling Frequency**: 19 Hz (prime number to avoid harmonic resonance with periodic tasks).
- **Transport**: Batched, compressed pprof format pushed asynchronously over gRPC with local backpressure drop.
- **Aggregation & Storage**: Centralized storage (e.g. Grafana Pyroscope or Parca) indexed by service name, environment, git commit SHA, and trace ID.
- **Correlation**: Injects TraceID/SpanID from OpenTelemetry into profiling context so developers can jump directly from a slow distributed trace to the exact flamegraph slice of that transaction.
