# Interview Questions: Performance Profiling

## Company-Specific Focus

### Google
- Performance analysis tools: async-profiler, JFR, JMC
- CPU profiling: sampling profilers vs tracing profilers
- Allocation profiling: finding hot allocation sites and GC pressure

### Microsoft
- Java performance: Azure Monitor, Application Insights for JVM
- Thread dump analysis: thread state, lock contention

### Amazon
- Profiling in production: async-profiler, JFR streaming
- Latency analysis: P99, P999, and application of queue delays
- Flame graphs: interpreting CPU and allocation profiles

### Meta
- Memory profiling: what leaks memory in the production system
- JIT compilation: how profiling data influences compilation decisions

### Apple
- Using the jcmd tool for on-demand profiling
- Understanding GC pauses: G1GC vs ZGC
- OS-level profiling: using perf on Linux to analyze the application

### Oracle
- JDK Flight Recorder (JFR): event collection and streaming
- JDK Mission Control (JMC): UI for analyzing JFR recordings
- jcmd, jstack, jmap, jhat: diagnostic tools
- Performance regression testing using JMH

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems - profiling is a diagnostic activity) |

## Real Production Scenarios
- **Netflix**: P99 latency spike found to be caused by ZGC nongenerational mode; migrated to generational ZGC
- **Uber**: CPU usage at 100% for 10 minutes after deployment — JIT compilation at tier 4 max
- **LinkedIn**: Memory leak in the ThreadLocal variable across request processing — fixed by using try-finally to remove ThreadLocal values

## Interview Patterns & Tips
- **Tools**: async-profiler, JFR, JMC, jstack, jmap, jcmd
- **Metric to watch**: GC pause time, allocation rate, code cache usage
- **Flame Graphs**: analyze CPU time and memory allocation
- **Continuous profiling**: JFR streaming for real-time analysis

## Deep Dive Questions
- **JFR**: How is JFR implemented? Low overhead, ring buffer based event recorder
- **async-profiler**: How does it work? Uses perf_events on Linux, ktrace on macOS
- **Sampling**: How does async-profiler collect call stacks? Uses signal-based sampling
- **JIT profiling**: How does the JVM profiling data influence JIT compilation decisions?
- **GC profiling**: How to identify the GC cause and its root cause in production