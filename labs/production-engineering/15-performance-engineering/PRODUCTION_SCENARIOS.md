# PRODUCTION SCENARIOS: Performance Engineering War Stories
## Lab 15 | Production Engineering Academy

---

## Scenario 1: The 10x Slowdown from False Sharing in High-Frequency Trading

### Context
An ultra-low-latency market data aggregator written in Java. The service processed 500,000 price quotes/sec across 4 worker threads pinned to physical cores.

### The Mystery
Engineers upgraded the server hardware from 4 cores to 16 cores. Instead of throughput quadrupling, throughput **dropped by 65%**, and CPU utilization hovered at 100% while processing fewer events!

### Root Cause Analysis via Linux `perf`
The team ran `perf c2c report` (Cache-to-Cache coherency analyzer):
- It revealed intense **HITM (Hit Modified)** events on a single cache line.
- The thread statistics tracking class had:
  ```java
  public class WorkerStats {
      public volatile long thread0Events;
      public volatile long thread1Events;
      public volatile long thread2Events;
      public volatile long thread3Events;
  }
  ```
- All 4 `long` variables (8 bytes each = 32 bytes total) fit inside a **single 64-byte cache line**!
- As 4 cores updated their respective event counters hundreds of thousands of times per second, the L1/L2 caches invalidated each other continuously. Cores spent 80% of their cycles stalling on inter-socket bus traffic.

### The Fix
Padded each counter to its own independent 64-byte cache line:
```java
public class PaddedCounter {
    // 56 bytes of padding before and after
    public long p1, p2, p3, p4, p5, p6, p7;
    public volatile long value;
    public long p8, p9, p10, p11, p12, p13, p14;
}
```
Throughput immediately leaped from 180,000 ops/sec to **3.8 million ops/sec** on the 16-core machine.

---

## Scenario 2: The JIT Megamorphic Call Deoptimization Collapse

### Context
A payment gateway processing card authorisations used a common interface: `PaymentProcessor.process()`.

### The Failure Mode
- For years, the production system ran with only 2 implementations: `StripeProcessor` and `AdyenProcessor` (Bimorphic call site). HotSpot C2 JIT inlined both implementations into high-speed direct branch checks.
- A junior engineer added a 3rd implementation (`PayPalProcessor`), making the call site **megamorphic** (> 2 implementations).
- HotSpot C2 could no longer inline the method; it had to deoptimize and fall back to expensive `vtable` dynamic virtual dispatch on every single request.
- Overall application throughput dropped by 22% fleet-wide.
