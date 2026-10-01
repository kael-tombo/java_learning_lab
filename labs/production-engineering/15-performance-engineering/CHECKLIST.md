# CHECKLIST: High-Performance Production Readiness & Mechanical Sympathy
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Hardware Architecture & Cache Alignment

- [ ] **False Sharing Elimination**:
  - [ ] All high-frequency concurrent mutable counters/cursors are padded with 56 bytes (7 longs) pre- and post-field or annotated with `@jdk.internal.vm.annotation.Contended`.
  - [ ] JVM started with `-XX:-RestrictContended` if using `@Contended` on application classes.
  - [ ] Verified zero high-frequency HITM events using `perf c2c record -p $PID` under peak synthetic load.
- [ ] **Contiguous Memory & Cache Prefetching**:
  - [ ] Hot path collections replaced with contiguous array structures (`ArrayList`, primitive arrays, or HPPC/FastUtil primitive buffers).
  - [ ] Zero usage of `LinkedList`, `TreeMap`, or deep pointer-chasing node graphs inside hot processing loops.
  - [ ] Data traversal patterns are sequential to ensure the L1/L2 hardware stream prefetcher achieves $\ge 85\%$ hit rates.
- [ ] **Branch Prediction & Monomorphic Call Sites**:
  - [ ] Critical polymorphic call sites audited to maintain monomorphic or bimorphic dispatch ($\le 2$ implementations).
  - [ ] High-frequency conditional loops operate on pre-sorted arrays where applicable to eliminate branch mispredictions.
  - [ ] Hardware branch miss rate verified via `perf stat` ($\text{branch-misses} / \text{branches} < 3\%$).

---

## 2. Memory Hygiene & Zero-Allocation Path

- [ ] **Allocation-Free Hot Path Contract**:
  - [ ] Inner packet, message, or order-processing loops verified to produce zero allocations in TLAB via `asprof -e alloc` flame graphs.
  - [ ] Intermediate calculation variables use primitive types (`long`, `double`) rather than boxed wrappers (`Long`, `Double`).
  - [ ] Strings are never dynamically concatenated (`+` or `StringBuilder`) inside hot loops; use pre-allocated byte slices or interned token enums.
- [ ] **Buffer and Off-Heap Pooling**:
  - [ ] Netty `ByteBuf` instances are released strictly inside `finally` blocks using `ReferenceCountUtil.release()`.
  - [ ] Netty Resource Leak Detector verified in pre-production with `-Dio.netty.leakDetection.level=PARANOID`.
  - [ ] Object pools (e.g. RingBufferObjectPool, Agrona RingBuffer) are pre-sized to power-of-2 capacities to leverage bitmask indexing.
- [ ] **Garbage Collector Health**:
  - [ ] GC CPU overhead verified to be $< 3\%$ of total process CPU usage under peak production load.
  - [ ] Zero Full GC events observed over a continuous 7-day rolling window.
  - [ ] Time-to-safepoint (TTSP) verified to be $< 2\text{ms}$ via `-Xlog:safepoint=debug`.

---

## 3. Concurrency, Locks & Threading Mechanics

- [ ] **Lock Contention Elimination**:
  - [ ] Synchronized blocks eliminated from all high-throughput paths in favor of CAS, `VarHandle`, or `StampedLock` optimistic reads.
  - [ ] Zero `synchronized` blocks inside Virtual Thread execution paths to prevent carrier thread pinning.
  - [ ] Lock hold times are strictly bounded ($< 1\mu\text{s}$) with zero I/O or network syscalls performed while holding locks.
- [ ] **CPU Affinity & NUMA Topology**:
  - [ ] Latency-critical threads pinned to dedicated physical CPU cores using `Affinity.setAffinity()` or `taskset`.
  - [ ] Threads communicating via shared ring buffers pinned to the same NUMA node to eliminate cross-socket QPI/UPI interconnect latency.
  - [ ] Host kernel configured with `isolcpus` for trading or sub-millisecond real-time workloads.

---

## 4. JIT Compilation & Profiling Standards

- [ ] **Microbenchmark Validation**:
  - [ ] Every performance optimization PR accompanied by a JMH benchmark suite.
  - [ ] Benchmark configured with minimum 5 warmup iterations, 10 measurement iterations, and 3 JVM forks.
  - [ ] All benchmark outputs consumed via `Blackhole.consume()` to prevent Dead Code Elimination.
- [ ] **Production Profiling Readiness**:
  - [ ] `async-profiler` installed and executable in all production and staging environments.
  - [ ] Linux kernel parameter `/proc/sys/kernel/perf_event_paranoid` configured to `1` or `0`.
  - [ ] Continuous JFR (Java Flight Recorder) enabled with rolling 100MB ring-buffer recording:
    ```bash
    -XX:StartFlightRecording=disk=true,dumponexit=true,filename=crash.jfr,maxsize=100m,maxage=24h
    ```

---

## 5. Linux Kernel & System Tuning

- [ ] **NIC & Network Stack**:
  - [ ] Network card hardware interrupts (IRQs) pinned to non-application cores via `/proc/irq/*/smp_affinity`.
  - [ ] Socket send/receive buffer sizes expanded via `sysctl`:
    ```bash
    net.core.rmem_max = 16777216
    net.core.wmem_max = 16777216
    ```
- [ ] **Zero-Copy File I/O**:
  - [ ] Bulk disk-to-network file transfers leverage `FileChannel.transferTo()` (sendfile syscall) rather than user-space heap byte buffers.
