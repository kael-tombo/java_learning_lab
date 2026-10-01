# INTERVIEW QUESTIONS: High-Performance Java & Mechanical Sympathy
## Lab 15 | Senior / Staff / Principal / Distinguished Engineer Level

---

## Senior Level (5–7 Years)

### Q1: What is False Sharing and how does it degrade Java concurrent performance?

**Answer:**
Modern CPUs cache memory in 64-byte chunks called **cache lines**. When two threads on different CPU cores each write to distinct variables that happen to reside within the same 64-byte memory region, the CPU's **MESI cache coherency protocol** triggers cross-core cache invalidation:

1. Thread A (Core 0) writes to `counter1` → Core 0 acquires "Modified" state of the shared cache line.
2. The MESI protocol broadcasts an **invalidation message** to all other cores.
3. Thread B (Core 1) must reload the entire cache line from L3/DRAM before accessing `counter2`.
4. Under high-frequency mutual writes, both cores spend the majority of their cycles waiting for bus arbitration — not doing actual work.

**Degradation magnitude**: In extreme cases, false sharing reduces multi-threaded throughput by **80–90%** compared to properly padded counters.

**Detection**: `perf c2c report` — look for high **HITM (Hit on Modified)** counts. Trace the address back to Java fields using JOL (Java Object Layout).

**Fix**: Use `@jdk.internal.vm.annotation.Contended` (requires `-XX:-RestrictContended`) or add 56-byte padding manually before and after the hot field to force it onto an isolated 64-byte cache line.

---

### Q2: What is the difference between `synchronized`, `ReentrantLock`, and `StampedLock`? When do you use each?

**Answer:**

| | `synchronized` | `ReentrantLock` | `StampedLock` |
|---|---|---|---|
| **Fairness** | Unfair (JVM selects arbitrarily) | Configurable (`fair=true`) | Unfair |
| **Try Lock** | No (always blocks) | Yes (`tryLock(timeout)`) | Yes |
| **Condition Variables** | `wait()/notify()` | Multiple `Condition` objects | No |
| **Optimistic Read** | No | No | **Yes** |
| **Virtual Thread Pinning** | **Yes — dangerous!** | No | No |
| **Readability** | Simple | Verbose | Complex |

**Use `synchronized`**: Simple sections with low contention, non-critical paths.  
**Use `ReentrantLock`**: When you need `tryLock()`, multiple conditions, or Virtual Thread compatibility.  
**Use `StampedLock`**: Read-heavy data structures where optimistic reads (try-read without any blocking) are valid. Optimistic reads have **zero cost** when no writer is active.

**Critical**: Never use `synchronized` inside a Virtual Thread hot path — it pins the virtual thread to its carrier OS thread, defeating the purpose of Project Loom.

---

### Q3: Why is `LinkedList` 50–100× slower than `ArrayList` for iteration on modern hardware?

**Answer:**
CPU performance is dominated by cache behavior. An `ArrayList` stores all elements in a **contiguous memory block**. When iterating, the CPU's **hardware prefetcher** detects the sequential access pattern and proactively loads upcoming elements from DRAM into L1/L2 cache before they are requested. The effective access latency is the L1 cache hit time: ~1ns.

A `LinkedList.Node<E>` is an independent heap object containing the `item` and a `next` pointer. After millions of GC cycles, nodes scatter across random DRAM addresses. Every node traversal follows a pointer to an **arbitrary memory address** — a guaranteed L3 cache miss ($10–20\text{ ns}$) or worse, a DRAM access ($50–100\text{ ns}$) per node. The prefetcher cannot predict random pointer chains.

**The math**: Iterating 1M elements:
- `ArrayList`: $1{,}000{,}000 / 16 = 62{,}500$ cache line loads (16 ints fit in 64 bytes).
- `LinkedList`: $1{,}000{,}000$ cache line loads (1 node per cache miss).
- **Result**: `LinkedList` requires **16× more DRAM bandwidth** for the same operation.

---

## Staff Level (8–12 Years)

### Q4: Explain how HotSpot JIT compiles monomorphic, bimorphic, and megamorphic call sites differently. What are the production implications of adding a third implementation to a hot interface?

**Answer:**
HotSpot C2 JIT profiles call sites and optimizes based on observed receiver types:

**Monomorphic** (1 type): C2 inlines the concrete method directly — no virtual dispatch. The call site becomes a direct machine code `CALL` or even fully inlined inline code. `~0.5ns`.

**Bimorphic** (2 types): C2 generates an inline cache: a two-branch `cmp/je` dispatch to two inlined implementations. Still very fast. `~1–2ns`.

**Megamorphic** (3+ types): C2 abandons inlining. The call site reverts to a full **vtable dispatch** — loading the class pointer, indexing the vtable, and making an indirect `CALL *vtable[slot]`. This is $3–5×$ slower per call AND prevents any inlining optimizations in the called method.

**Production Impact**: Adding a 3rd `PaymentProcessor` implementation to a hot payment pipeline can drop fleet throughput by **15–25%** without any algorithmic change. Engineers who do not understand JIT compilation mechanics introduce silent regressions.

**Solutions**:
1. Restructure so the hot path is always monomorphic (route non-standard processors to a slow path).
2. Use sealed interfaces to help C2 enumerate all implementations.
3. Profile first with async-profiler to confirm the call site IS hot before optimizing.

---

### Q5: Describe the full lifecycle of a Java object allocation — from TLAB, through Eden, Survivor, to Old Generation. At what points does latency occur?

**Answer:**

**Step 1 — TLAB Bump Pointer Allocation** (Fastest path, ~1ns):
The thread has a private `Thread-Local Allocation Buffer` (TLAB) — a pre-carved slice of Eden assigned exclusively to it. Allocation is a single pointer increment: `tlab.top += objectSize`. No synchronization needed.

**Step 2 — TLAB Refill** (CAS on shared Eden cursor, ~100ns under contention):
When the TLAB fills, the thread requests a new TLAB from the Eden allocator. This requires a CAS operation on the shared Eden allocation cursor.

**Step 3 — Minor GC / Young Generation Collection** (Stop-the-world, 5–50ms):
When Eden fills, a Young GC pauses all threads. Reachable objects in Eden + Survivor-from are copied to Survivor-to. Short-lived objects (most Java objects) die here — "live cheap, die young."

**Step 4 — Tenuring to Old Generation**:
Objects surviving `MaxTenuringThreshold` (default 15) Minor GCs are promoted to Old Gen (G1: Old regions; ZGC: tenured space).

**Step 5 — Major/Mixed GC** (Concurrent marking, then stop-the-world evacuation):
G1 initiates concurrent marking when Old Gen hits `InitiatingHeapOccupancyPercent` (45% default). This runs concurrently. Evacuation pauses copy live objects from collected old regions — pause targets `MaxGCPauseMillis` (200ms default).

**Step 6 — Full GC Fallback** (CATASTROPHIC, 5–45 seconds):
If concurrent marking cannot finish before Old Gen is full, G1 falls back to a serial Full GC. This is a complete stop-the-world event and typically indicates the application is over-allocating or heap is undersized.

**The takeaway**: Latency occurs at TLAB refill (minor), Minor GC (significant), and Full GC (catastrophic). Allocation-free hot paths eliminate steps 1–4 entirely.

---

### Q6: You see this in async-profiler output: your hot path spends 40% of time in `java.lang.Object.hashCode()`. What does this indicate and how do you fix it?

**Answer:**
`Object.hashCode()` (the default identity hash code) is computed **lazily on first call** and then stored in the object header's Mark Word. However, the Mark Word has multiple purposes:

- Unlocked object: Mark Word stores identity hash code.
- Biased-locked object: Mark Word stores thread ID.
- Heavy-locked object: Mark Word stores pointer to lock record.

**The Problem**: If an object has been **biased-locked** (thread holds a biased lock) and then `hashCode()` is called on it, the JVM must **revoke the biased lock** to free up the Mark Word bits for the hash code. Bias lock revocation requires a **safepoint stop-the-world**!

At scale: if millions of objects require hash code computation + biased lock revocation per second, the JVM spends a disproportionate amount of time pausing all threads for safepoints.

**Fix**:
1. Disable biased locking: `-XX:-UseBiasedLocking` (default off in JDK 15+, removed in JDK 21).
2. Override `hashCode()` in your domain objects with a meaningful field-based implementation.
3. Or use `System.identityHashCode()` pre-cached in a field if identity semantics are required.
4. Use `HashMap` keys that are primitive-friendly (e.g., `LongObjectHashMap` from HPPC to avoid boxing).

---

## Principal / Distinguished Engineer Level (12+ Years)

### Q7: You inherit a Java service with P99 = 800ms. Your SLA requires P99 < 20ms. Describe your complete performance investigation methodology.

**Answer — The 5-Layer Systematic Approach**:

**Layer 1: Establish Measurement Baseline** (1 hour)
```bash
# Capture baseline latency distribution with percentiles
# Look for bimodal distribution: most requests fast, some slow (GC? Lock convoy?)
cat /proc/$(pgrep java)/status | grep -E "VmRSS|VmSwap"  # Memory usage
```

**Layer 2: GC Profiling — Eliminate GC as Root Cause** (2 hours)
```bash
java -Xlog:gc*:file=/tmp/gc.log:time,uptime,level,tags:filesize=100m PID
# Enable JFR for GC events:
jcmd PID JFR.start duration=120s filename=/tmp/gc_profile.jfr
```
Analyze: Minor GC frequency, Mixed GC pause times, Full GC occurrences (= bug), promotion failure (= heap sizing issue).

**Layer 3: CPU Profiling — async-profiler** (2 hours)
```bash
./asprof -d 120 -f /tmp/cpu_flame.html $(pgrep java)
```
Look for: Lock contention (identify the exact lock class), serialization hot spots, unexpected allocation sites, GC threads competing for CPU.

**Layer 4: Hardware Counter Profiling — Linux perf** (2 hours)
```bash
perf stat -p $(pgrep java) -e cycles,instructions,cache-misses,branch-misses sleep 60
perf c2c record -p $(pgrep java) -- sleep 30; perf c2c report
```
Look for: IPC < 0.5 (memory stalls), cache miss rate > 15% (pointer chasing), high HITM (false sharing), high branch mispredictions (megamorphic callsites).

**Layer 5: Concurrency Analysis — Thread Dumps + JFR Lock Events**
```bash
jcmd PID Thread.print > /tmp/threads.txt  # Identify BLOCKED threads
# JFR lock contention events:
jcmd PID JFR.start settings=profile duration=60s filename=/tmp/locks.jfr
```
Look for: Threads blocked on `synchronized`, `ReentrantLock`, database connection pool exhaustion, HTTP client connection pool saturation.

**The typical root cause distribution** (based on real investigations):
- GC pressure / heap sizing: 35% of cases
- Lock contention (database pool, cache client): 30%
- Pointer-chasing / data structure choice: 15%
- N+1 queries / missing index: 12%
- False sharing / thread affinity: 5%
- JIT deoptimization: 3%

---

### Q8: Design a lock-free, GC-free, multi-producer single-consumer order matching engine that can sustain 10M orders/second at P99 < 1μs. What are the architectural constraints?

**Answer — The Complete Architecture**:

**Constraints**:
1. **Zero GC**: No object allocation in hot path — pre-allocate all order objects.
2. **Lock-Free**: No kernel-blocking synchronization — only CAS-based algorithms.
3. **NUMA-Aware**: Pin producer and consumer threads to the same NUMA node.
4. **CPU Core Isolation**: Isolate matcher thread via `isolcpus` kernel parameter.
5. **Busy-Spin Wait**: Matcher uses `BusySpinWaitStrategy` — never parks.

**Architecture**:
```
[Producer Threads × N] ──────────────────────────────────►
                           ┌──────────────────────────┐
                           │   Disruptor Ring Buffer   │
                           │   (MPSC: Multi-Producer  │
                           │    Single Consumer)       │
                           │   Size: 2^20 = 1M slots   │
                           │   Pre-allocated OrderEvent│
                           └──────────────────────────┘
                                        │
                           ┌────────────▼───────────────┐
                           │   Order Matcher Thread     │
                           │   (Pinned to Core 5)       │
                           │   BusySpinWaitStrategy     │
                           │   Processes batch of N     │
                           └────────────┬───────────────┘
                                        │
                           ┌────────────▼───────────────┐
                           │   Trade Event Disruptor    │
                           │   (SPSC: matched trades)   │
                           └────────────────────────────┘
```

**Key implementation decisions**:
1. **OrderEvent fields are primitives only** (`long orderId`, `long price`, `int quantity`, `byte side`) — no String, no boxed types.
2. **Price is stored as `long` in `ticks`** (price × 10000) — eliminates floating-point precision issues and enables integer arithmetic.
3. **Order Book is an `int[]`-indexed array** indexed by price tick level — $O(1)$ price lookup, cache-friendly.
4. **Wait strategy**: `BusySpinWaitStrategy` burns one full CPU core but achieves sub-microsecond latency. Acceptable only for one critically latency-sensitive thread.
5. **Batch publishing**: Producers publish in batches using `RingBuffer.next(batchSize)` — reduces CAS contention by up to 90%.

**Throughput analysis**: At 10M orders/second:
- 10M × 64 bytes (OrderEvent) = 640 MB/s throughput requirement.
- L3 cache size = 32MB — ring buffer of 512K slots × 64B = 32MB fits exactly in L3!
- With ring buffer entirely in L3 cache: each slot access = ~15ns → theoretical max = $1 / 15\text{ns} = 66\text{M ops/sec}$, comfortably exceeding target.
