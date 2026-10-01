# PRODUCTION SCENARIOS: Performance Engineering War Stories & Real-World Outages
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The 10× Slowdown from False Sharing in High-Frequency Market Making

### 1. Incident Context & Architecture
- **Service**: `market-quote-feed-gateway`
- **Throughput SLA**: 1,200,000 market quotes/sec per node, P99 $\le 15\mu\text{s}$.
- **Hardware**: AWS `c6i.16xlarge` (64 vCPUs, 128 GiB RAM, 2 NUMA nodes).
- **Runtime**: OpenJDK 21 LTS with G1GC, 16 worker threads pinned to physical cores.

### 2. The Anomaly
Following a scheduled cloud instance upgrade from 8 physical cores to 32 physical cores to accommodate higher trading volume:
- Maximum throughput **collapsed from 480,000 ops/sec down to 142,000 ops/sec** (a 70% throughput drop).
- Top reported CPU usage showed all 16 worker cores pegged at **100% utilization**.
- Latency P99 jumped from **$11\mu\text{s}$ to $420\mu\text{s}$** without any GC pauses or network drops.

### 3. Triage & Root Cause Timeline
- **T+00:15**: Thread dumps verified no deadlocks, no OS blocking (`RUNNABLE` state across all workers).
- **T+00:30**: `perf stat` revealed an catastrophic Instruction-Per-Cycle (IPC) metric:
  ```text
  Cycles:        192,482,004,118
  Instructions:   17,323,380,370
  IPC:                      0.09  (Stalled on memory bus > 91% of clock cycles!)
  ```
- **T+00:45**: Execution of Linux `perf c2c record -p $PID -- sleep 10` followed by `perf c2c report`:
  ```text
  Shared Data Cache Line Table:
  Line Addr         HitM   Remote HitM  Data Address
  0x7f4b82103fa0    41920        29480  com.learning.trading.WorkerStats
  ```
  A single memory address accounted for **82% of all cache coherency bus invalidations (HITM)** across the NUMA nodes!

### 4. Code Autopsy
The per-thread transaction counter class had been written as:
```java
// CRITICAL BUG: All fields packed into one 48-byte object layout!
public class WorkerStatistics {
    public volatile long worker0Ticks;  // Offset 16 (8 bytes)
    public volatile long worker1Ticks;  // Offset 24 (8 bytes)
    public volatile long worker2Ticks;  // Offset 32 (8 bytes)
    public volatile long worker3Ticks;  // Offset 40 (8 bytes)
}
```
All four worker threads were writing to their respective counter variables millions of times per second. Because all four fields fit inside a **single 64-byte L1 cache line**, each core's write triggered a MESI hardware cache invalidation bus broadcast across all other cores. The cores spent 91% of their operational time stalled on cache coherency bus arbitration!

### 5. Production Remediation & Verification
```java
// Production Fix: Cache-line isolation via manual 56-byte dummy padding
public class WorkerStatistics {
    // 56 bytes padding before value
    private long p00, p01, p02, p03, p04, p05, p06;
    public volatile long worker0Ticks;
    private long p08, p09, p10, p11, p12, p13, p14; // 56 bytes padding after

    private long p10a, p11a, p12a, p13a, p14a, p15a, p16a;
    public volatile long worker1Ticks;
    private long p18, p19, p20, p21, p22, p23, p24;
}
```
*Outcome*:
- IPC immediately surged from **0.09 to 2.14**.
- Throughput on the 32-core instance leaped to **2,850,000 ops/sec** (a 20× increase).
- P99 dropped to **$4.8\mu\text{s}$**.

---

## Scenario 2: Megamorphic Virtual Dispatch Deoptimization in Payment Engine

### 1. Incident Context & Architecture
- **Service**: `global-payment-orchestrator`
- **Workload**: 40,000 transactions/sec HTTP REST API.
- **Incident**: After deploying a feature branch integrating a third payment provider (Klarna), average CPU load surged by 38% fleet-wide, and P99 latency breached SLA limits (jumped from 18ms to 74ms).

### 2. Investigation & Flame Graph Discrepancy
- Profiling with `async-profiler` before the release showed `PaymentRouter.route()` taking **0.3% of CPU**.
- After the release, `PaymentRouter.route()` and interface dispatch accounted for **18.7% of total CPU cycles**.
- JIT log review with `-XX:+PrintCompilation -XX:+TraceDeoptimization`:
  ```text
  128442 3911 % ! 4   com.learning.pay.PaymentRouter::process @ 12 (48 bytes)
  128448 3911   uncommon_trap: reason=class_check action=make_not_entrant
  128449 3912   4   com.learning.pay.PaymentRouter::process (made not entrant)
  ```

### 3. Root Cause Analysis
Prior to the release, the payment router had only two implementations:
```java
public interface PaymentGateway {
    PaymentResult execute(PaymentRequest req);
}
// 1. StripeGateway
// 2. AdyenGateway
```
HotSpot C2 JIT had optimized `execute()` as a **bimorphic inline cache**:
```assembly
# JIT Compiled Pseudo-Assembly for Bimorphic Call:
cmp  rax, [StripeGateway.class]
je   inlined_stripe_code
cmp  rax, [AdyenGateway.class]
je   inlined_adyen_code
# Fast direct jumps! Both targets fully inlined into the caller frame.
```

When `KlarnaGateway` was added, the number of distinct concrete types passing through the call site reached **3**. HotSpot C2 classified the call site as **megamorphic**:
- C2 completely tore down the compiled method frame (`made not entrant`).
- Inlining was revoked.
- Re-compilation fell back to standard indirect `vtable` lookup:
  ```assembly
  mov  rax, [rcx + 0x08]       # Load Klass pointer from object header
  mov  rax, [rax + 0x140]      # Load vtable array
  call [rax + 0x20]           # Indirect call via pointer — defeats branch target buffer (BTB)
  ```
- Because inlining was gone, compiler optimizations inside `process()` (dead-code elimination, escape analysis, scalar replacement) collapsed simultaneously.

### 4. Architectural Resolution
Decouple the routing layer so each processing path is strictly **monomorphic**:
```java
public class HighThroughputPaymentRouter {
    private final StripeGateway stripe = new StripeGateway();
    private final AdyenGateway adyen = new AdyenGateway();
    private final KlarnaGateway klarna = new KlarnaGateway();

    public PaymentResult route(PaymentRequest req) {
        // Concrete dispatch via enum branch instead of polymorphic interface:
        return switch (req.provider()) {
            case STRIPE -> stripe.executeDirect(req); // Monomorphic call site — C2 inlines!
            case ADYEN  -> adyen.executeDirect(req);  // Monomorphic call site — C2 inlines!
            case KLARNA -> klarna.executeDirect(req); // Monomorphic call site — C2 inlines!
        };
    }
}
```
*Outcome*: Inlining was fully restored; fleet CPU load dropped by 36% immediately.

---

## Scenario 3: Safepoint Stalls Caused by Counted Loop Unrolling

### 1. Incident Context
- **Service**: `risk-calculation-engine`
- **Symptom**: Periodic "stop-the-world" latency spikes of **1,200ms** occurred every 30 seconds.
- **Confusion**: GC logs showed total garbage collection pause times were under **8ms**!
  ```text
  [0.820s][info][gc] GC(42) Pause Young (Normal) (G1 Evacuation Pause) 7.82ms
  ```
  If GC paused for only 7.82ms, why did HTTP clients experience a 1,200ms stall?

### 2. Deep Dive: Time-To-Safepoint (TTSP)
The engineering team enabled Safepoint diagnostic logging:
```bash
-XX:+UnlockDiagnosticVMOptions -XX:+PrintSafepointStatistics -XX:PrintSafepointStatisticsCount=1
# Or in modern JDKs:
-Xlog:safepoint=debug:file=/var/log/jvm/safepoint.log:time,uptime,level,tags
```
The safepoint log revealed:
```text
[2026-09-24T14:12:02.102+0000] Safepoint "G1CollectForAllocation", 
  Time to safepoint: 1192 ms,  Total pause: 1201 ms
```
The JVM spent **1,192ms simply trying to bring all threads to a halt** before GC could even start!

### 3. Root Cause: Counted Loop Without Safepoint Poll
In HotSpot C2, integer counted loops (`for (int i = 0; i < N; i++)`) have their safepoint polling checks stripped by default for performance:
```java
// Risk analysis thread calculating Monte Carlo simulation:
for (int i = 0; i < 2_000_000_000; i++) {
    // Heavy computation without any safepoint polls:
    matrix[i % 1024] += compute(i);
}
```
When a worker thread entered this loop:
1. GC requested a safepoint.
2. All other threads reached a safepoint and paused immediately.
3. The Monte Carlo thread could not pause until its loop fully completed (or hit an uncounted branch)!
4. The entire JVM froze for 1.2 seconds waiting on this single thread.

### 4. Permanent Remediation
Enable **Loop Strip Mining** (default in JDK 10+, but requires verification if tuned off):
```bash
-XX:+UseCountedLoopSafepoints
```
Or rewrite the loop with a long induction variable (`for (long i = 0; i < N; i++)`), which HotSpot treats as an uncounted loop and retains the safepoint poll instruction at each iteration:
```java
// Long induction variable guarantees a safepoint poll instruction
for (long i = 0; i < N; i++) {
    matrix[(int)(i % 1024)] += compute(i);
}
```
*Outcome*: Time-to-safepoint dropped to **$0.4\text{ms}$**, eliminating the multi-second client stalls entirely.

---

## Scenario 4: The Off-Heap Netty DirectBuffer Memory Exhaustion Cascade

### 1. Incident Context
- **Service**: `realtime-push-websocket-server`
- **Workload**: 200,000 active concurrent WebSocket connections on Netty.
- **Incident**: Kubernetes nodes continuously crashed with `Exit Code 137` (Linux OOM-Killer). Java heap usage was only 4 GiB out of 16 GiB container limit!

### 2. Diagnosis via Native Memory Tracking (NMT)
```bash
jcmd $PID VM.native_memory baseline
# 20 minutes later:
jcmd $PID VM.native_memory detail.diff
```
*NMT Diff Output*:
```text
-    Internal (reserved=9420MB +4120MB, committed=9420MB +4120MB)
              (malloc=9420MB +4120MB #38290 +14200)
```
The off-heap memory was growing by 200 MB per minute until the Linux kernel terminated the container.

### 3. Root Cause: Missing Netty ReferenceCountUtil.release()
In an asynchronous filter pipeline:
```java
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    ByteBuf buffer = (ByteBuf) msg;
    if (shouldDrop(buffer)) {
        // BUG: Dropping packet without release!
        // DirectByteBuffer allocated via jemalloc remains pinned in off-heap memory!
        return; 
    }
    ctx.fireChannelRead(msg);
}
```
Because `ByteBuf` references in Netty use reference counting, failing to call `ReferenceCountUtil.release(msg)` leaves the backing off-heap direct memory permanently allocated.

### 4. Resolution & Safeguard
```java
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    try {
        ByteBuf buffer = (ByteBuf) msg;
        if (shouldDrop(buffer)) {
            return; // Finally block guarantees deallocation!
        }
        ctx.fireChannelRead(ReferenceCountUtil.retain(msg));
    } finally {
        ReferenceCountUtil.release(msg);
    }
}
```
Enabled Netty resource leak detection in staging:
```bash
-Dio.netty.leakDetection.level=PARANOID
```
*Outcome*: Off-heap memory plateaued stably at 1.8 GiB under 200,000 active connections.
