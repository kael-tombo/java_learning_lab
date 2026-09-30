# ARCHITECTURE DECISIONS: JVM Memory & Garbage Collector Selection
## Lab 01 | Production Engineering Academy

---

## ADR-01: Selection of Default Garbage Collector for Microservices

### Status: ACCEPTED / PRODUCTION STANDARD

### Context
Our microservices fleet consists of 450+ Java applications running on Kubernetes (EKS / GKE) on x86_64 and ARM64 (AWS Graviton) compute nodes. Services vary in profile:
- 70% stateless REST/gRPC APIs (heap sizes 2 GB – 8 GB, p99 latency target < 25ms)
- 20% high-throughput streaming consumers (Kafka/Flink, heap sizes 8 GB – 32 GB, throughput prioritized over tail latency)
- 10% memory-intensive analytical / caching services (heap sizes 32 GB – 128 GB, p99 latency target < 100ms)

Historically, applications defaulted to ParallelGC on small instances and un-tuned G1GC on larger instances, leading to unpredictable tail latencies and occasional 2-4 second Stop-The-World (STW) pauses during major compaction events.

### Decision Drivers
1. **Predictable Tail Latency (p99 / p99.9)**: Financial trading and checkout pipelines must avoid pause spikes.
2. **Operational Overhead**: Developers must not need to tune 25 obscure JVM flags per service.
3. **Throughput vs Latency Trade-off**: CPU overhead of concurrent collectors vs STW collectors.
4. **Memory Footprint & Fragmentation**: Low physical memory footprint in multi-tenant Kubernetes clusters.
5. **Java LTS Support**: Alignment with OpenJDK 17 and OpenJDK 21.

### Options Considered

#### Option 1: Parallel GC (`-XX:+UseParallelGC`)
- *Pros*: Maximum throughput; lowest CPU overhead for GC work; optimal for batch jobs.
- *Cons*: Stop-The-World pauses scale directly with heap size (e.g., 500ms to 5s pauses on 16GB heaps); unacceptable for real-time customer APIs.

#### Option 2: G1 GC (`-XX:+UseG1GC`)
- *Pros*: Highly mature, industry standard since Java 9; predictable pause times with `-XX:MaxGCPauseMillis`; excellent ergonomics; compacts regions dynamically.
- *Cons*: Can still experience full GC fallbacks under heavy allocation spikes; tail pauses can still exceed 50-100ms on large heaps.

#### Option 3: Generational ZGC (`-XX:+UseZGC -XX:+ZGenerational` in Java 21+)
- *Pros*: Sub-millisecond pause times (< 1ms STW pauses) independent of heap size (tested up to terabytes); concurrent mark, evacuate, and reference processing; modern generational architecture in Java 21.
- *Cons*: Requires ~10-15% higher CPU overhead due to read/load barriers; requires slightly larger heap headroom (15-20%) to prevent allocation stalls; requires Java 21+.

#### Option 4: Shenandoah GC (`-XX:+UseShenandoahGC`)
- *Pros*: Ultra-low pause times with concurrent evacuation; available on both Java 11 and 17 in certain distributions.
- *Cons*: Brooks pointers / load-reference barriers add CPU overhead; Generational Shenandoah is still evolving; less uniform support across vendor JDKs compared to ZGC.

### Decision Outcome
We standardize on a **two-tier Garbage Collector policy**:

1. **Standard Latency-Sensitive Tier (Default for all Web/gRPC APIs, Java 21+)**:
   - Collector: **Generational ZGC** (`-XX:+UseZGC -XX:+ZGenerational`)
   - Heap rule: Container limits $\ge$ 4 GiB, `-XX:MaxRAMPercentage=70.0`.
   - Reason: Eliminates latency spikes, achieving p99.9 GC pause times under 1ms without developer flag tuning.

2. **Throughput-Oriented / Memory-Constrained Tier (Batch jobs, Kafka bulk ingest, containers < 2 GiB)**:
   - Collector: **G1 GC** (`-XX:+UseG1GC`)
   - Flags: `-XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:InitiatingHeapOccupancyPercent=45`
   - Reason: ZGC requires additional headroom and CPU threads for concurrent workers which degrades performance on small 1-2 vCPU containers.

---

## ADR-02: Container Memory Allocation & Sizing Strategy

### Status: ACCEPTED

### Context
Containerized JVMs frequently suffered `Exit Code 137` (Linux OOM killer `SIGKILL`) due to discrepancy between cgroup limits and JVM heap configuration.

### Decision
1. **Dynamic Cgroup Awareness**:
   - Use `-XX:+UseContainerSupport` (enabled by default in modern JDKs).
   - Use percentage-based heap sizing:
     - `-XX:InitialRAMPercentage=70.0`
     - `-XX:MaxRAMPercentage=70.0`
     (Setting Initial equal to Max prevents JVM heap resizing stalls in production).
2. **Explicit Overhead Budgeting (Remaining 30%)**:
   - Metaspace: `-XX:MaxMetaspaceSize=384m`
   - Code Cache: `-XX:ReservedCodeCacheSize=256m`
   - Direct Memory: `-XX:MaxDirectMemorySize=512m` (if Netty/gRPC used)
   - Stack Memory: budget $1\text{ MB} \times \text{Max Threads}$.
3. **Crash Diagnostics**:
   - Mandate:
     ```bash
     -XX:+HeapDumpOnOutOfMemoryError
     -XX:HeapDumpPath=/dumps/oom-%p.hprof
     -XX:+CrashOnOutOfMemoryError
     ```
   - All Kubernetes Pods must mount a persistent or ephemeral dump volume at `/dumps`.

### Consequences
- Eliminates manual JVM heap flag changes when adjusting Kubernetes CPU/memory requests.
- Protects workloads from abrupt kernel OOM kills.
- Guarantees immediate actionable forensic dumps upon `OutOfMemoryError`.
