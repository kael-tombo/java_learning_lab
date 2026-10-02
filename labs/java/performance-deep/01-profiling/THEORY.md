# THEORY — Java Profiling Fundamentals

## Overview

Profiling is the systematic measurement of a program's runtime behavior—CPU usage, memory allocation, thread activity, I/O patterns—to identify bottlenecks and optimize performance. In production Java systems, profiling is not a one-time activity but a continuous feedback loop.

---

## 1. Profiling Dimensions

| Dimension | What It Measures | Typical Tools |
|-----------|------------------|---------------|
| **CPU** | Time spent in methods, hot paths | async-profiler, JFR, JProfiler |
| **Memory** | Allocation rates, object sizes, GC pressure | JFR, VisualVM, JProfiler, async-profiler |
| **Thread** | Contention, blocking, starvation | JFR, async-profiler, jstack |
| **GC** | Pause times, frequency, heap occupancy | GC logs, JFR, GC logs |
| **I/O** | File/socket throughput, latency | iostat, JFR, eBPF |

---

## 2. Profiling Methodologies

| Method | Overhead | Use Case |
|--------|----------|----------|
| **Sampling** | Low (1-5%) | Production, continuous |
| **Instrumentation** | High (10-50%+) | Dev/test, detailed counts |
| **Tracing** | Variable | Distributed systems, latency analysis |

### Sampling Profilers

- **async-profiler**: Low-overhead, uses `perf_events` + JVMTI, supports CPU, memory, lock, wall-clock
- **JFR (JDK Flight Recorder)**: Built-in, ~1-2% overhead, rich event model
- **Java Flight Recorder (JFR)**: JDK 8u40+, continuous recording

### Instrumentation Profilers

- **JProfiler / YourKit**: Bytecode instrumentation, method-level timings
- **VisualVM**: Built-in, good for development

---

## 3. Profiling Workflow

```
1. Define Goal          → "Reduce p99 latency by 30%"
2. Establish Baseline   → Current p50/p99/p99.9, throughput, error rate
3. Profile              → Collect data under representative load
4. Analyze              → Identify top 3 bottlenecks (Pareto)
5. Hypothesize          → "GC pauses cause p99 spikes"
6. Experiment           → Tune GC, change algorithm, add cache
7. Validate             → Compare against baseline
8. Automate             → Add regression test, alert on regression
```

---

## 4. Key Metrics

| Metric | Healthy Range | Action If Exceeded |
|--------|---------------|-------------------|
| CPU utilization | < 70% sustained | Profile hot methods |
| GC pause (p99) | < 50ms | Tune GC, reduce allocation |
| GC frequency | < 1/min (young) | Increase heap, reduce allocation |
| Heap utilization | < 70% | Investigate leaks, tune GC |
| Thread count | < 2x cores | Check blocking, pool sizing |
| p99 latency | < SLA | Profile hot path |

---

## 5. Profiling Tools Comparison

| Tool | Overhead | Best For | Learning Curve |
|------|----------|----------|----------------|
| async-profiler | 1-2% | Prod CPU/memory/lock | Low |
| JFR | 1-2% | Prod all-around | Medium |
| JProfiler | 10-30% | Deep dive, dev | Low |
| YourKit | 10-20% | Memory/CPU, dev | Low |
| VisualVM | 5-15% | Quick look, dev | Low |
| JFR + JDK Mission Control | 1-2% | Prod analysis | Medium |