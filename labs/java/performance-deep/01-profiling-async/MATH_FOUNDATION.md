# MATH_FOUNDATION — Async Profiling Mathematics

## 1. Virtual Thread Throughput Model

### Throughput Model

```
Throughput = (Virtual Threads × Utilization) / (Latency + Overhead)
```

Where:
- Virtual Threads = configured parallelism × carrier utilization
- Utilization = 1 - (Pinning Probability + Blocking Probability)
- Overhead = Context switch + Scheduling + Pinning penalty

### Pinning Cost Model

```
Pinning Cost = Pinning Frequency × Pin Duration × Carrier Threads
```

If 10% of virtual threads pin for 10ms each, on 100 carrier threads:
- 10% × 10ms = 1ms effective carrier loss per virtual thread
- At 1000 virtual threads/100 carriers: 10% carrier capacity lost

---

## 1. Virtual Thread Queueing Model

### M/M/∞ Approximation (Unbounded Virtual Threads)

Since virtual threads are cheap, model as M/M/∞:

```
Throughput = min(Arrival Rate, Virtual Threads / Latency)
Queue Length = Arrival Rate × Latency (if Arrival > Throughput)
```

**Key insight**: Virtual threads decouple concurrency from thread count — bottleneck shifts to downstream (DB, CPU, network).

### Pinning Impact

```
Effective Throughput = Throughput × (1 - Pinning Probability)
```

If 5% of requests pin for 10ms at 1000 req/s:
- 50 req/s pin for 10ms → 50 threads blocked → capacity loss

---

## 2. Structured Concurrency Mathematics

### StructuredTaskScope Reliability

For `n` parallel tasks with failure probability `p`:

```
P(any failure) = 1 - (1-p)^n
Expected failures = n × p
```

With `ShutdownOnFailure`: expected cancelled tasks = `n × p` (approximately)

### Cancellation Cascade

Failure in one fork → cancel all others → expected wasted work:
```
Wasted Work = Σ (Remaining Work of Cancelled Tasks)
```

**Design principle**: Keep forked tasks short and idempotent.

---

## 2. Concurrency Mathematics

### Virtual Thread Concurrency

```
Concurrency = RPS × Latency / Concurrency_Per_Instance
```

With virtual threads:
- Concurrency no longer bounded by thread pool size
- Limited by: memory, CPU, downstream capacity, pinning

### Little's Law for Async Systems

```
Concurrency = Throughput × Latency
```

For async systems with virtual threads:
- Max concurrency = available memory / stack size
- Practical limit: heap pressure, GC, downstream saturation

---

## 2. Async Context Propagation Overhead

### Context Copy Cost

```
Context Copy Cost = Context_Size × Propagation_Frequency
```

Typical OpenTelemetry context: ~1-2 KB. At 10,000 req/s:
- 2 KB × 10,000 = 20 MB/s allocation
- Mitigation: context pooling, lazy propagation

---

## 2. Structured Concurrency Reliability

### Failure Probability

For `n` parallel tasks, each with failure probability `p`:

```
P(any failure) = 1 - (1-p)^n
Expected failures = n × p
```

With `ShutdownOnFailure`: cancelled tasks ≈ `n × p`

### Cancellation Waste

```
Wasted Work = Σ (Remaining Work of Cancelled Tasks)
```

**Design principle**: Keep forked tasks short and idempotent.

---

## 3. Backpressure Mathematics

### Little's Law for Async Systems

```
Concurrency = Throughput × Latency
```

For reactive systems:
- `Throughput` = requests/sec processed
- `Latency` = end-to-end (including queue time)
- `Concurrency` = in-flight requests

**Capacity Planning**: Target latency `L`, desired throughput `T` → need concurrency `C = T × L`.

### Backpressure Flow

```
Producer → [Buffer] → Consumer
    ↑              ↓
    └── request(n) ←
```

Consumer signals demand via `request(n)`. Producer respects demand.

### Buffer Sizing

```
Buffer Size ≥ RTT × Throughput
```

Too small → backpressure stalls producer. Too large → memory pressure, latency.

---

## 3. Backpressure & Flow Control

### Little's Law for Reactive Systems

```
Concurrency = Throughput × Latency
```

For reactive systems with backpressure:
- `Throughput` = requests/sec processed
- `Latency` = end-to-end (including queue time)
- `Concurrency` = in-flight requests

### Backpressure Flow

```
Producer → [Buffer] → Consumer
    ↑              ↓
    └── request(n) ←
```

Consumer signals demand via `request(n)`. Producer respects demand.

### Buffer Sizing

```
Buffer Size ≥ RTT × Throughput
```

Too small → backpressure stalls producer. Too large → memory pressure, latency.

---

## 4. Queueing Theory for Async Systems

### M/M/1 Queue (Single Consumer)

- Arrival rate: λ
- Service rate: μ
- Utilization: ρ = λ/μ
- Mean queue length: L = ρ/(1-ρ)
- Mean wait time: W = 1/(μ-λ)

**Design rule**: Keep ρ < 0.7 for stable latency.

### M/M/c Queue (c Consumers)

- Utilization: ρ = λ/(cμ)
- Queue probability: Erlang C formula
- Mean wait: Wq = P(queue) / (cμ - λ)

---

## 5. Virtual Thread Scalability Limits

### Memory Model

```
Memory = (Stack_Size × Virtual_Threads) + Heap + Metaspace + Code_Cache
```

Default stack: 1MB (configurable via `-Xss`). 1M virtual threads = 1TB virtual memory (committed ~few GB).

### Carrier Thread Utilization

```
Carrier_Utilization = (Active_VT × VT_CPU_Time) / Carrier_Threads
```

Target: > 80% carrier utilization.

### Pinning Overhead

```
Pinning_Overhead = Pin_Probability × Pin_Duration / Request_Latency
```

Target: < 5% pinning overhead.

---

## 6. Reactive Streams Mathematics

### Backpressure Flow Control

```
Producer → [request(n)] → Consumer
Consumer → [request(n)] → Producer
```

Consumer signals demand. Producer respects demand.

### Flow Control Stability

For stable system:
```
Producer_Rate ≤ Consumer_Rate × (1 - Buffer_Utilization)
```

If producer consistently faster → buffer grows → OOM or latency spike.

### Buffer Sizing

```
Buffer_Size ≥ RTT × Throughput
```

Too small → backpressure stalls producer. Too large → memory pressure, latency.

---

## 6. Cost Models

### Thread vs Virtual Thread

| Metric | Platform Thread | Virtual Thread |
|--------|----------------|----------------|
| Stack | 1 MB (fixed) | ~1 KB (grows) |
| Creation | ~10-50 μs | ~1-5 μs |
| Context Switch | ~1-5 μs | ~0.1-1 μs |
| Max Count | ~10,000 | Millions |
| Pinning Risk | None | Synchronized, native, I/O |

### Cost per Request

```
Cost = (Stack_Allocation + Context_Switch + Scheduling) / Request
```

Virtual threads: ~5-10× cheaper for I/O-bound workloads.

---

## 7. Scaling Laws

### Amdahl's Law for Async

```
Speedup = 1 / ((1 - f) + f/s)
```

Where `f` = parallelizable fraction, `s` = speedup of parallel portion.

Virtual threads increase `f` (more concurrent I/O), but `s` limited by downstream.

### Universal Scalability Law

```
Throughput(N) = N / (1 + α(N-1) + βN(N-1))
```

- α = contention
- β = coherency delay

Virtual threads reduce α (less locking), but β may increase (more coordination).

---

## Summary: Key Ratios

| Ratio | Healthy | Warning | Critical |
|-------|---------|---------|----------|
| Pinning % | < 1% | 1-5% | > 5% |
| Carrier Utilization | 60-80% | 80-95% | > 95% |
| Virtual Thread / Carrier | 100:1 | 1000:1 | > 10000:1 |
| Allocation Rate | < 100 MB/s | 100-500 MB/s | > 500 MB/s |
| GC Pause (p99) | < 10 ms | 10-50 ms | > 50 ms |
| Thread Pool ρ | < 0.7 | 0.7-0.9 | > 0.9 |

---

*End of MATH_FOUNDATION — Async Profiling Mathematics*