# ARCHITECTURE DECISIONS: High-Performance Architecture Standards
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Mandatory JMH for Performance-Critical PRs

### Status: ACCEPTED

### Context
Ad-hoc benchmarks using `System.currentTimeMillis()` produced wildly inaccurate measurements, leading to incorrect optimization decisions. A senior engineer once "proved" a new serialization format was 10× faster — it was actually measuring an empty JIT-eliminated loop. The "optimized" version shipped and degraded production P99 by 35%.

### Decision
**Any PR claiming a performance improvement on a hot path MUST include a JMH benchmark** proving the improvement under realistic conditions.

**Benchmark Requirements**:
1. Warmup: Minimum 5 iterations × 1 second each.
2. Measurement: Minimum 10 iterations × 1 second each.
3. Fork: Minimum 3 separate JVM processes (`@Fork(3)`).
4. `Blackhole.consume()` on all computed values to prevent Dead Code Elimination.
5. Results show improvement at `p < 0.01` statistical significance (JMH provides error intervals).

**PR template addition**:
```markdown
## Performance Impact
- Benchmark: `com.example.benchmarks.MyBenchmark`
- Metric: Average Time (ns/op)
- Before: 243 ± 12 ns/op
- After: 89 ± 4 ns/op
- Improvement: 2.73× throughput gain (p=0.003)
```

### Consequences
- Eliminates subjective performance claims.
- Adds 1–2 hours to P-Crit optimization PRs — acceptable cost.
- Forces engineers to deeply understand what they are measuring.

---

## ADR-02: Contiguous-Memory-First Data Structure Policy

### Status: ACCEPTED

### Context
A code audit revealed widespread use of `LinkedList` and `HashMap<Long, Object>` in hot paths. A single microservice was creating 40+ million `LinkedList.Node` objects per minute, causing 6–8 Minor GC pauses per minute and ~200ms P99 spikes per GC cycle.

### Decision
**Hot path data structures must use array-backed, contiguous-memory layouts**:

| Use Case | Forbidden | Required |
|---|---|---|
| Ordered Collection | `LinkedList<T>` | `ArrayList<T>`, `ArrayDeque<T>` |
| Long Key Map | `HashMap<Long, V>` | `LongObjectHashMap<V>` (HPPC/EclipseCollections) |
| Int Key Map | `HashMap<Integer, V>` | `IntObjectHashMap<V>` |
| Sorted Set | `TreeSet<T>` | `int[]` + `Arrays.binarySearch()` for static sets |
| Priority Queue | `PriorityQueue<T>` | `int[]`-based heap with explicit indexing |

**Exception**: `LinkedList` and `HashMap` permitted in:
- Application startup / initialization code.
- Test fixtures.
- Non-hot admin/management code paths.

### Rationale (Cache Math)
An `ArrayList` iterating 1M integers loads $1{,}000{,}000 / 16 = 62{,}500$ cache lines from L3/DRAM.
A `LinkedList` iterating 1M integers loads $1{,}000{,}000$ cache lines (one per node pointer chase) — **16× more DRAM traffic**.

### Consequences
- Reduces GC pressure by eliminating per-element object allocation.
- Requires HPPC or EclipseCollections as project dependency.
- `int[]`-backed sorted sets require custom binary search utilities — provide team-shared `CollectionUtils`.

---

## ADR-03: Allocation-Free Hot Path Contract

### Status: ACCEPTED

### Context
A trading engine hot path (order book update) was creating $> 1$ billion objects per hour under load. With G1GC, Eden space filled every 2.1 seconds triggering Minor GC pauses of 15–40ms, making P99 SLA compliance (< 10ms) impossible.

### Decision
**Designated hot paths must be validated as allocation-free** using one of:
1. **JFR Allocation Profiling**: Enable `jdk.ObjectAllocationInNewTLAB` JFR event and verify no events fire inside the hot path boundary.
2. **Google Allocation Instrumenter**: `@NoAllocation` annotation (from `com.google.code.java-allocation-instrumenter`) throws `AssertionError` at test time if any allocation occurs inside the annotated method.
3. **JVM `-verbose:gc` monitoring**: If Minor GC frequency < 1 per minute under peak load, the allocation rate is acceptable.

**Object Reuse Strategies**:
```java
// Strategy A: Ring Buffer of Pre-Allocated Objects (LMAX Disruptor style)
private final OrderEvent[] ringBuffer = new OrderEvent[RING_SIZE]; // Pre-allocated
static { for (int i = 0; i < RING_SIZE; i++) ringBuffer[i] = new OrderEvent(); }

// Strategy B: ThreadLocal Object Pool (for per-thread request contexts)
private static final ThreadLocal<RequestContext> CONTEXT_POOL =
    ThreadLocal.withInitial(RequestContext::new);
// ... use, reset(), reuse (call CONTEXT_POOL.remove() at request end)
```

### Consequences
- Dramatically reduces GC pressure on Eden space.
- Requires pre-sizing all in-memory buffers at startup.
- Immutable value objects and records are still fine outside hot paths.
- Adds testing complexity — allocation-free tests must run in single-threaded JMH fork.

---

## ADR-04: Mechanical Sympathy-Aware Thread Affinity

### Status: ACCEPTED

### Context
The LMAX-style event processing pipeline showed unexpected $15\mu\text{s}$ jitter spikes on P99. Analysis with `perf sched` revealed OS threads were being migrated between NUMA nodes by the Linux CFS scheduler, causing L3 cache cold-start penalties on every migration.

### Decision
**Latency-critical threads must be pinned to specific CPU cores** using OS thread affinity:

```java
// Using Java Native Access (JNA) or Affinity library (Peter Lawrey):
import net.openhft.affinity.Affinity;

// Pin the current thread to Core 3, preventing OS scheduler migration:
Affinity.setAffinity(1L << 3);  // CPU mask: bit 3 = core 3
```

**NUMA Topology Requirements**:
- Identify NUMA node topology: `numactl --hardware`
- Pin all threads of a pipeline to the **same NUMA node** to ensure L3 cache sharing and minimize cross-NUMA memory bus traffic.
- Isolate "noisy" GC threads on a separate NUMA node from the latency-critical application threads.

**CPU Isolation (at OS level)**:
```bash
# Kernel boot parameter: isolate cores 4-7 from OS scheduler
GRUB_CMDLINE_LINUX="isolcpus=4-7 rcu_nocbs=4-7 nohz_full=4-7"
```
Isolated cores are never preempted by the OS scheduler — the application has exclusive access.

### Consequences
- P99 jitter reduced from 15μs to < 2μs in HFT workloads.
- Requires dedicated CPU topology planning for multi-service deployments.
- `isolcpus` requires Linux kernel restart — coordinate with platform team.
- Not required for non-latency-critical services.

---

## ADR-05: Async Profiler as Standard Production Profiler (No safepoint-bias)

### Status: ACCEPTED

### Context
Engineers were using VisualVM's CPU sampler, which uses JVMTI safepoint-based sampling. This creates **safepoint bias**: samples are only taken at safepoints (method entry/exit, backward branches). Long CPU-bound loops without safepoints are **invisible** to JVMTI samplers — the most performance-critical code is precisely what cannot be profiled!

### Decision
**async-profiler** is the mandatory CPU profiler for all production performance investigations:

```bash
# Profile PID for 60 seconds, generate flame graph SVG:
./asprof -d 60 -f /tmp/flamegraph.html $(pgrep java)
```

async-profiler uses OS-level signals (`SIGPROF`) to interrupt threads at arbitrary points, including inside tight CPU-bound loops. It accurately captures:
- Time spent in JIT-compiled native frames.
- JVM runtime frames (GC, compilation, JIT code cache flushing).
- Native library frames (Netty epoll, SSL, malloc).
- Kernel time (system calls, page faults, context switches).

**Additional modes**:
```bash
# Memory allocation profiling (find allocation hot spots):
./asprof -e alloc -d 60 -f /tmp/alloc.html PID

# Lock contention profiling:
./asprof -e lock -d 60 -f /tmp/locks.html PID
```

### Consequences
- async-profiler reveals the *true* CPU hot spots, including GC thread time, native library overhead, and kernel time invisible to JVMTI profilers.
- Requires the `perf_event_paranoid` kernel parameter to be `<= 1`.
- Java agents: `-agentpath:/path/to/libasyncProfiler.so=start,event=cpu,file=/tmp/profile.jfr`
